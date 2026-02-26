from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from helpers import get_setting, Settings
from pipelines.SavaalPipeline import SavaalPipeline
from controllers import MainIdeaController
from models import ResponseSignal, MainIdeaModel, ChunkModel
from models.db_schemas import MainIdea
from bson.objectid import ObjectId
from .schemes import MainIdeaExtractionRequest, MainIdeaExtractionResponse, MainIdeaResponse, MainIdeasListResponse, QuestionGenerationRequest, QuestionGenerationResponse
import logging
from datetime import datetime, timezone


logger = logging.getLogger(__name__)


# Router setup
savaal_router = APIRouter(
    prefix="/api/v1/savaal",
    tags=["savaal"]
)

@savaal_router.post(
    "/extract/{project_id}",
    response_model=MainIdeaExtractionResponse,
    status_code=status.HTTP_200_OK
)
async def extract_main_ideas(
    request: Request,
    project_id: str,
    extraction_request: MainIdeaExtractionRequest,
    settings: Settings = Depends(get_setting)
):
    """
    Start main idea extraction pipeline for a document.
    
    Pipeline Steps:
    1. Get chunks from database by file_id
    2. Group chunks into sections (each chunk is a section)
    3. Extract candidate ideas from each section in parallel
    4. Consolidates and deduplicates ideas
    5. Ranks ideas by importance
    6. Associates relevant chunks with each idea via vector search
    7. Saves everything to database
    """
    try:
        logger.info(f"Main idea extraction requested: project={project_id}, file={extraction_request.file_id}")
        
        # Validate project ID
        try:
            project_oid = ObjectId(project_id)
        except Exception:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                  "signal": ResponseSignal.PROJECT_NOT_FOUND.value,
                }
            )
        
        # Get chunks from database by file_id
        chunk_model = await ChunkModel.create_instance(request.app.state.db_client)
        chunks = await chunk_model.get_chunks_by_asset_id(asset_id=ObjectId(extraction_request.file_id))

        if not chunks:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.GET_CHUNKS_BY_ASSET_ID_ERROR.value,
                }
            )
        
        # Group chunks into sections (each chunk is a section)
        sections = [chunk.chunk_text for chunk in chunks]
        
        # Run extraction pipeline (extract → combine → reduce → rank)
        
        # Initialize pipeline
        pipeline = SavaalPipeline(
            db_client=request.app.state.db_client,
            vectordb_client=request.app.state.vectordb_client,
            llm_client=request.app.state.generation_client,
            embedding_client=request.app.state.embedding_client,
            template_parser=request.app.state.template_parser,
            project_id=project_id)
        
        
        # Run extraction pipeline
        result = await pipeline.run_main_idea_extraction(sections=sections)
        
        # Associate chunks to each ideas
        main_ideas = result["main_ideas"]
        ranked_ideas = result["ranked_ideas"]
        
        idea_chunk_mapping = await pipeline.associate_chunks_to_ideas(
            main_ideas=main_ideas,
            ranked_ideas=ranked_ideas,
            top_k_chunks=extraction_request.top_k_chunks
        )
        
        # Save to database
        main_idea_model = await MainIdeaModel.create_instance(request.app.state.db_client)
        saved_count = await pipeline.save_main_ideas(
            main_ideas=main_ideas,
            ranked_ideas=ranked_ideas,
            idea_chunk_mapping=idea_chunk_mapping,
            main_idea_model=main_idea_model
        )
        
        
        response = {
            "signal": ResponseSignal.MAIN_IDEA_EXTRACTION_SUCCESS.value,
            "sections_count": len(sections),
            "candidates_count": result.get("extracted_candidates_count", 0),
            "consolidated_count": result.get("combined_candidates_count", 0),
            "main_ideas_count": result.get("final_count", 0),
            "chunk_associations_count": sum(len(v) for v in idea_chunk_mapping.values()),
        }
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response
        )
        
    except Exception as e:
        logger.error(f"Error in main idea extraction: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": ResponseSignal.MAIN_IDEA_EXTRACTION_FAILED.value,
                "sections_count": 0,
                "candidates_count": 0,
                "consolidated_count": 0,
                "main_ideas_count": 0,
                "chunk_associations_count": 0
            }
        )

@savaal_router.get(
    "/main-ideas/{project_id}",
    response_model=MainIdeasListResponse,
    status_code=status.HTTP_200_OK
)
async def get_main_ideas(
    request: Request,
    project_id: str,
    limit: int = 0,
    settings: Settings = Depends(get_setting)
):
    """
    Get all main ideas for a project.
    
    Retrieves ranked main ideas along with their associated chunk counts.
    
    Args:
        project_id: MongoDB ObjectId of the project
        limit: Maximum number of ideas to return (0 = no limit)
        
    Returns:
        List of main ideas with metadata
    """
    try:
        logger.info(f"Retrieving main ideas: project={project_id}, limit={limit}")
        
        # Validate project ID
        try:
            project_oid = ObjectId(project_id)
        except Exception:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.PROJECT_NOT_FOUND.value,
                    "project_id": project_id,
                    "main_ideas_count": 0,
                    "main_ideas": [],
                }
            )
        
        # Retrieve ideas from database
        main_idea_model = await MainIdeaModel.create_instance(request.app.state.db_client)
        ideas = await main_idea_model.get_project_main_ideas(
            project_id=project_oid,
            top=limit if limit > 0 else 0
        )
        
        # Convert to response format
        ideas_response = [
            MainIdeaResponse(
                id=str(idea.id),
                title=idea.main_idea_name,
                summary=idea.main_idea_summary,
                rank=idea.main_idea_rank,
                chunk_count=len(idea.main_idea_chunk_ids) if idea.main_idea_chunk_ids else 0
            )
            for idea in ideas
        ]
        
        # Sort by rank if available
        ideas_response.sort(key=lambda x: x.rank if x.rank else 999)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.MAIN_IDEA_RETRIEVAL_SUCCESS.value,
                "project_id": project_id,
                "main_ideas_count": len(ideas_response),
                "main_ideas": [
                    {
                        "id": idea.id,
                        "title": idea.title,
                        "summary": idea.summary,
                        "rank": idea.rank,
                        "chunk_count": idea.chunk_count
                    }
                    for idea in ideas_response
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"Error retrieving main ideas: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": ResponseSignal.MAIN_IDEA_RETRIEVAL_FAILED.value,
                "project_id": project_id,
                "main_ideas_count": 0,
                "main_ideas": [],
            }
        )


@savaal_router.post(
    "/generate/{project_id}",
    response_model=QuestionGenerationResponse,
    status_code=status.HTTP_200_OK
)
async def generate_questions(
    request: Request,
    project_id: str,
    generation_request: QuestionGenerationRequest,
    settings: Settings = Depends(get_setting)
):
    """
    Generate questions from main ideas.
    
    This endpoint generates different types of questions (MCQ, T/F, Short Answer)
    based on main ideas and their associated document chunks.
    
    Args:
        project_id: MongoDB ObjectId of the project
        generation_request: Request parameters
        
    Returns:
        Generation results with statistics
    """
    try:
        logger.info(f"Question generation requested: project={project_id}, "
                   f"types={generation_request.question_types}")
        
        # Validate project ID
        try:
            project_oid = ObjectId(project_id)
        except Exception:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": "failed",
                    "message": f"Invalid project ID: {project_id}",
                    "ideas_processed": 0,
                    "questions_generated": 0,
                    "questions_by_type": {}
                }
            )
        
        # Initialize pipeline
        pipeline = SavaalPipeline(
            db_client=request.app.state.db_client,
            vectordb_client=request.app.state.vectordb_client,
            project_id=project_id,
            llm_provider=request.app.state.generation_client,
            embedding_provider=request.app.state.embedding_client,
            template_parser=request.app.state.template_parser
        )
        
        # Run question generation
        result = await pipeline.run_question_generation(
            project_id=project_id,
            main_idea_ids=generation_request.main_idea_ids,
            question_types=generation_request.question_types,
            questions_per_idea=generation_request.questions_per_idea
        )
        
        response = {
            "status": result["status"],
            "ideas_processed": result["ideas_processed"],
            "questions_generated": result["questions_generated"],
            "questions_by_type": result["questions_by_type"],
            "message": f"Question generation {'completed' if result['status'] == 'success' else 'failed'}: "
                      f"generated {result['questions_generated']} questions"
        }
        
        if result["errors"]:
            response["errors"] = result["errors"]
        
        status_code = status.HTTP_200_OK if result["status"] == "success" else status.HTTP_400_BAD_REQUEST
        
        return JSONResponse(
            status_code=status_code,
            content=response
        )
        
    except Exception as e:
        logger.error(f"Error in question generation: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "failed",
                "message": f"Error during question generation: {str(e)}",
                "ideas_processed": 0,
                "questions_generated": 0,
                "questions_by_type": {}
            }
        )
