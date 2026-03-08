from fastapi import APIRouter, Depends, status, Request, Query
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import MainIdeaController, ProcessController, NLPController
from models import ResponseSignal
from models.MainIdeaModel import MainIdeaModel
from models.ProjectModel import ProjectModel
from models.AssetModel import AssetModel
from models.db_schemas import MainIdea, MainIdeaChunk
from models.MainIdeaChunkModel import MainIdeaChunkModel
from models.enums import AssetTypeEnum
from stores.llm.templates.template_parser import PromptTemplateParser
from langchain_core.documents.base import Document
from typing import List
from bson.objectid import ObjectId
from .schemes import MainIdeaExtractionRequest, MainIdeaExtractionResponse, MainIdeasListResponse, QuestionGenerationRequest, QuestionGenerationResponse, AssociateChunksRequest, AssociateChunksResponse
import logging


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
  settings: Settings = Depends(get_settings)
):
  """
  Start main idea extraction pipeline for a document.
  
  Pipeline Steps:
  1. Get chunks from database by asset_name
  2. Group chunks into sections (each chunk is a section)
  3. Extract candidate ideas from each section in parallel
  4. Consolidates and deduplicates ideas
  5. Ranks ideas by importance
  6. Saves everything to database
  """
  logger.info(f"Main idea extraction requested: project={project_id}, file={extraction_request.asset_name}")

  # Get project
  project_model = await ProjectModel.create_instance(db_client=request.app.state.db_client)
  project = await project_model.get_project_or_create_one(project_id=project_id)
  
  # Get project assets
  asset_model = await AssetModel.create_instance(db_client=request.app.state.db_client)
  if extraction_request.asset_name:
    assets = [await asset_model.get_asset_record(
      asset_project_id=project.id,
      asset_name=extraction_request.asset_name
    )]
  else:
    assets = await asset_model.get_all_project_assets(
      asset_project_id=project.id,
      asset_type=AssetTypeEnum.FILE.value
    )
  
  if not assets or assets == [None]:
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content = {
        "signal" : ResponseSignal.NO_FILES_IDS.value,
      }
    )
  
  # Split assets into sections
  process_controller = ProcessController(project_id=project_id)
  texts: List[Document] = []
  for asset in assets:
    file_content = process_controller.get_file_content(file_id=asset.asset_name)
    if file_content is None:
      logger.warning(f"File content is None for asset: {asset.asset_name}")
      continue
    
    texts.extend(
      process_controller.process_file_content(
        file_content=file_content,
        file_id=None,
        chunk_size=extraction_request.section_size
      )
    )
  sections = [doc.page_content for doc in texts]
  
  # Run extraction pipeline (extract → combine → reduce → rank)
  prompt_template_parser = PromptTemplateParser(
    domain=project.domain,
    language=project.language.value,
  )
  
  main_idea_controller = MainIdeaController(
    generation_client=request.app.state.generation_client,
    embedding_client=request.app.state.embedding_client,
    prompt_template_parser=prompt_template_parser
  )
  
  # Run extraction precedure
  logger.info(f"Extracting candidate ideas from {len(sections)} sections")
  candidates = await main_idea_controller.extract_candidates_from_sections(sections=sections)

  # Run combining procedure
  logger.info(f"Combining and deduplicating {len(candidates)} candidate ideas")
  candidates = await main_idea_controller.combine_candidates(candidates=candidates)
  
  if extraction_request.limit is not None:
    # Run reducing procedure
    logger.info(f"Reducing {len(candidates)} combined ideas to top {extraction_request.limit}")
    candidates = await main_idea_controller.reduce_candidates(
      candidates=candidates,
      limit=extraction_request.limit
    )
  
  # Save to database
  logger.info(f"Saving {len(candidates)} main ideas to database for project {project_id}")
  main_idea_model = await MainIdeaModel.create_instance(request.app.state.db_client)
  
  main_idea_records = []
  for cand in candidates:
    main_idea_obj = MainIdea(
      main_idea_project_id=project.id,
      main_idea_name=cand.name[:100],
      main_idea_summary=cand.summary,
    )
    main_idea_records.append(main_idea_obj)
  
  if main_idea_records:
    
    # Reset existing main ideas and associations if requested
    if extraction_request.do_reset:
      logger.info(f"Resetting main ideas for project {project_id}")
      
      # Delete all associations for each main idea
      main_idea_chunk_model = await MainIdeaChunkModel.create_instance(request.app.state.db_client)

      deleted_count = await main_idea_chunk_model.delete_many_associations_by_project_id(project_id=project.id)
      logger.info(f"Deleted {deleted_count} associations for project {project_id}")
      
      # Delete all main ideas for the project
      deleted_count = await main_idea_model.delete_many_main_ideas_by_project_id(project_id=project.id)
      logger.info(f"Deleted {deleted_count} main ideas for project {project_id}")
    
    # Save new main ideas
    saved_count = await main_idea_model.insert_many_main_ideas(main_ideas=main_idea_records)
    logger.info(f"Successfully saved {saved_count} main ideas")
  else:
    
    logger.warning("No main idea records to save")
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={
      "signal": ResponseSignal.MAIN_IDEA_EXTRACTION_FAILED.value,
      "sections_count": len(sections),
      "main_ideas_count": len(candidates),
      }
    )
  
  
  return JSONResponse(
    status_code=status.HTTP_200_OK,
    content={
      "signal": ResponseSignal.MAIN_IDEA_EXTRACTION_SUCCESS.value,
      "sections_count": len(sections),
      "main_ideas_count": len(candidates),
    }
  )



@savaal_router.post(
  "/associate/{project_id}",
  response_model=AssociateChunksResponse,
  status_code=status.HTTP_200_OK
)
async def associate_chunks_to_ideas(
  request: Request,
  project_id: str,
  association_request: AssociateChunksRequest,
  settings: Settings = Depends(get_settings)
):
  """
  Associate vector-DB chunks to each main idea via semantic search.

  For every main idea (or the subset given in main_idea_ids), the summary
  is embedded and the top-k nearest chunks are retrieved from the project
  collection, then persisted as MainIdeaChunk records.
  """
  logger.info(f"Chunk association requested: project={project_id}, top_k={association_request.top_k}")

  # Get project
  project_model = await ProjectModel.create_instance(db_client=request.app.state.db_client)
  project = await project_model.get_project_or_create_one(project_id=project_id)

  # Retrieve main ideas
  main_idea_model = await MainIdeaModel.create_instance(request.app.state.db_client)

  if association_request.main_idea_ids:
    ideas = [
      await main_idea_model.get_main_idea_record(idea_id)
      for idea_id in association_request.main_idea_ids
    ]
    ideas = [idea for idea in ideas if idea is not None]
  else:
    ideas = await main_idea_model.get_project_main_ideas(project_id=project.id)

  if not ideas:
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={
        "signal": ResponseSignal.MAIN_IDEA_RETRIEVAL_FAILED.value,
        "ideas_processed": 0,
        "total_associations": 0,
      }
    )

  # Build NLP controller for vector search
  nlp_controller = NLPController(
    vectordb_client=request.app.state.vectordb_client,
    generation_client=request.app.state.generation_client,
    embedding_client=request.app.state.embedding_client,
    template_parser=request.app.state.template_parser,
  )

  # Get embedding model name
  embedding_model = getattr(request.app.state.embedding_client, "embedding_model_id", "unknown")

  # Prepare MainIdeaChunk model
  main_idea_chunk_model = await MainIdeaChunkModel.create_instance(request.app.state.db_client)

  # Drop old associations
  deleted_count = await main_idea_chunk_model.delete_many_associations_by_project_id(project_id=project.id)
  logger.info(f"Deleted {deleted_count} associations for project id: {project.id}")

  total_associations = 0
  for idea in ideas:
    search_results = nlp_controller.search_chunks_metadata(
      project=project,
      text=idea.main_idea_summary,
      limit=association_request.top_k
    )

    if not search_results:
      logger.warning(f"No search results for idea: {idea.id} - '{idea.main_idea_summary[:30]}...'")
      continue

    # Create MainIdeaChunk records
    associations = []
    for rank, res in enumerate(search_results, start=1):
      association = MainIdeaChunk(
        main_idea_id=idea.id,
        project_id=project.id,
        chunk_id=ObjectId(res["metadata"].get("db_id")),
        similarity_score=res["score"],
        retrieval_rank=rank,
        embedding_model=embedding_model,
      )
      associations.append(association)

    # Bulk insert all associations
    if associations:
      await main_idea_chunk_model.insert_many_associations(associations=associations)
      total_associations += len(associations)
      logger.info(f"Pushed {len(associations)} associations")

  logger.info(f"Chunk association complete: {total_associations} associations across {len(ideas)} ideas")

  return JSONResponse(
    status_code=status.HTTP_200_OK,
    content={
      "signal": ResponseSignal.MAIN_IDEA_EXTRACTION_SUCCESS.value,
      "ideas_processed": len(ideas),
      "total_associations": total_associations,
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
  limit: int = Query(0, description="Maximum number of ideas to return (0 = no limit)"),
  settings: Settings = Depends(get_settings)
):
  """
  Get all main ideas for a project.

  Retrieves main ideas along with their associated chunk counts.

  Args:
      project_id: MongoDB ObjectId of the project
      limit: Maximum number of ideas to return (0 = no limit)

  Returns:
      List of main ideas with metadata
  """
  logger.info(f"Retrieving main ideas: project={project_id}, limit={limit}")

  # Get project
  project_model = await ProjectModel.create_instance(db_client=request.app.state.db_client)
  project = await project_model.get_project_or_create_one(project_id=project_id)

  # Retrieve ideas from database
  main_idea_model = await MainIdeaModel.create_instance(request.app.state.db_client)
  ideas = await main_idea_model.get_project_main_ideas(
    project_id=project.id,
    top=limit if limit > 0 else 0
  )

  if not ideas:
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={
        "signal": ResponseSignal.NO_MAIN_IDEAS_FOUND.value,
        "project_id": project_id,
        "main_ideas": [],
      }
    )

  # Convert to response format
  ideas_response = [
    {
      "id": str(idea.id),
      "title": idea.main_idea_name,
      "summary": idea.main_idea_summary,
      "rank": idea.main_idea_rank,
      "chunk_count": len(idea.main_idea_chunk_ids) if idea.main_idea_chunk_ids else 0
    }
    for idea in ideas
  ]

  # Sort by rank if available
  ideas_response.sort(key=lambda x: x["rank"] if x["rank"] else 999)

  return JSONResponse(
    status_code=status.HTTP_200_OK,
    content={
      "signal": ResponseSignal.MAIN_IDEA_RETRIEVAL_SUCCESS.value,
      "project_id": project_id,
      "main_ideas": ideas_response,
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
    settings: Settings = Depends(get_settings)
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
                "ideas_processed": 0,
                "questions_generated": 0,
                "questions_by_type": {}
            }
        )
