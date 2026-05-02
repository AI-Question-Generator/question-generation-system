from fastapi import APIRouter, Depends, status, Request, Query
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import MainIdeaController, ProcessController, NLPController, QuestionController
from models import ResponseSignal
from models.MainIdeaModel import MainIdeaModel
from models.ProjectModel import ProjectModel
from models.AssetModel import AssetModel
from models.ChunkModel import ChunkModel
from models.db_schemas import MainIdea, MainIdeaChunk
from models.MainIdeaChunkModel import MainIdeaChunkModel
from models.enums import AssetTypeEnum
from stores.llm.templates.response_models.questions import BaseQuestion
from stores.llm.templates.template_parser import PromptTemplateParser
import stores.llm.templates.response_models as rm
from langchain_core.documents.base import Document
from typing import List
from bson.objectid import ObjectId
from .schemes import (
  MainIdeaExtractionRequest,
  MainIdeaExtractionResponse,
  MainIdeasListResponse,
  MainIdeaResponse,
  MainIdeaRankRequest,
  MainIdeaRankResponse,
  QuestionGenerationRequest,
  QuestionGenerationResponse,
  AssociateChunksRequest,
  AssociateChunksResponse,
  BatchQuestionGenerationRequest,
  BatchQuestionGenerationResponse,
  ProjectGenerationResult,
  GenerationResult,
  )
import asyncio
import logging


logger = logging.getLogger('uvicorn.error')


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
  if association_request.do_reset:
    deleted_count = await main_idea_chunk_model.delete_many_associations_by_project_id(project_id=project.id)
    logger.info(f"Deleted {deleted_count} associations for project id: {project.id}")

  total_associations = 0
  for idea in ideas:
    search_results = await nlp_controller.search_chunks_metadata(
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

  if total_associations == 0: # No associations done
    return JSONResponse(
      status_code=status.HTTP_200_OK,
      content={
        "signal": ResponseSignal.MAIN_IDEA_RETRIEVAL_FAILED.value,
        "ideas_processed": len(ideas),
        "total_associations": total_associations,
      }
    )
  
  return JSONResponse(
    status_code=status.HTTP_200_OK,
    content={
      "signal": ResponseSignal.MAIN_IDEA_RETRIEVAL_SUCCESS.value,
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
      project_id: String id of the project
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
  ideas_response = MainIdeasListResponse(
    signal=ResponseSignal.MAIN_IDEA_RETRIEVAL_SUCCESS.value,
    project_id=project_id,
    main_ideas=[
      MainIdeaResponse(
        id= str(idea.id),
        title=idea.main_idea_name,
        summary=idea.main_idea_summary,
        rank=idea.main_idea_rank,
      )
      for idea in ideas
    ]
  )

  return ideas_response

@savaal_router.post(
  "/rank/{project_id}",
  response_model=MainIdeaRankResponse,
  status_code=status.HTTP_200_OK,
)
async def rank_main_ideas(
  request: Request,
  project_id: str,
  ranking_request: MainIdeaRankRequest,
  settings: Settings = Depends(get_settings)
):
  logger.info(f"ranking main ideas: project={project_id}")

  # Get project
  project_model = await ProjectModel.create_instance(db_client=request.app.state.db_client)
  project = await project_model.get_project_or_create_one(project_id=project_id)

  # Retrieve ideas from database
  main_idea_model = await MainIdeaModel.create_instance(request.app.state.db_client)
  ideas = await main_idea_model.get_project_main_ideas(
    project_id=project.id,
  )
  
  # Rank Ideas
  prompt_template_parser = PromptTemplateParser(
    domain=project.domain,
    language=project.language.value,
  )
  main_idea_controller = MainIdeaController(
    generation_client=request.app.state.generation_client,
    embedding_client=request.app.state.embedding_client,
    prompt_template_parser=prompt_template_parser,
  )
  ranks = await main_idea_controller.rank_main_ideas(ideas=[rm.MainIdea(name=idea.main_idea_name, summary=idea.main_idea_summary) for idea in ideas])

  # Update ideas ranks
  if len(ranks) != len(ideas):
    print("here")
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={
        "signal": ResponseSignal.MAIN_IDEA_RANKING_FALIED.value,
        "ranked_count": 0
      }
    )
  
  # Push into db
  main_idea_model = await MainIdeaModel.create_instance(db_client=request.app.state.db_client)
  ranked_count = await main_idea_model.update_many_ranks_by_id(main_idea_ids=[idea.id for idea in ideas], ranks = ranks)
  
  if ranked_count is None:
    return JSONResponse(
      status_code=status.HTTP_200_OK,
      content={
        "signal": ResponseSignal.MAIN_IDEA_RANKING_FALIED.value,
        "ranked_count": 0
      }
    )
  
  return JSONResponse(
    status_code=status.HTTP_200_OK,
    content={
      "signal": ResponseSignal.MAIN_IDEA_RANKING_SUCCESS.value,
      "ranked_count": ranked_count
    }
  )


@savaal_router.post(
  "/generate",
  response_model=BatchQuestionGenerationResponse,
  status_code=status.HTTP_200_OK
)
async def batch_generate_questions(
  request: Request,
  batch_request: BatchQuestionGenerationRequest,
  settings: Settings = Depends(get_settings)
):
  """
  Generate questions in batch from main ideas for multiple projects.
  """
  logger.info(f"Batch question generation requested for {len(batch_request.tasks)} projects.")

  # Build Models
  project_model = await ProjectModel.create_instance(db_client=request.app.state.db_client)
  main_idea_model = await MainIdeaModel.create_instance(db_client=request.app.state.db_client)
  main_idea_chunk_model = await MainIdeaChunkModel.create_instance(db_client=request.app.state.db_client)
  chunk_model = await ChunkModel.create_instance(db_client=request.app.state.db_client)

  overall_results = []

  for project_task in batch_request.tasks:
    project_id = project_task.project_id
    project_results = []
    
    project = await project_model.get_project_or_create_one(project_id=project_id)
    
    # Build controllers
    prompt_template_parser = PromptTemplateParser(
      domain=project.domain,
      language=project.language.value,
    )
    question_controller = QuestionController(
      generation_client=request.app.state.generation_client,
      prompt_template_parser=prompt_template_parser,
    )

    # Process generation requests
    for generation_request in project_task.requests:
      main_ideas_count = await main_idea_model.count_main_ideas_by_project_id(project_id=project.id)

      if main_ideas_count == 0: # No main ideas for this project
        logger.error(f"Error generating questions for project {project_id}, type {generation_request.question_type.value}: Project has no main ideas.")
        project_results.append(GenerationResult(
          question_type=generation_request.question_type.value,
          questions=QuestionGenerationResponse(
              signal=ResponseSignal.QUESTION_GENERATION_FAILED.value,
              ideas_processed=0,
              questions_generated=[]
            )
        ))
        continue

      if main_ideas_count > generation_request.num_questions:
        # Put a question for each main idea
        main_ideas = await main_idea_model.get_project_main_ideas_sample(project_id=project.id, sample_size=generation_request.num_questions)
        questions_per_idea = [1] * len(main_ideas)
      else:
        # Distribute number of questions over main ideas
        main_ideas = await main_idea_model.get_project_main_ideas(project_id=project.id)
        questions_per_idea = [generation_request.num_questions // main_ideas_count] * main_ideas_count
        for i in range(generation_request.num_questions % main_ideas_count):
          questions_per_idea[i] += 1

      q_tasks = []
      for main_idea, q_count in zip(main_ideas, questions_per_idea):
        if q_count == 0:
          continue
        
        context_chunks = await main_idea_chunk_model.get_chunks_for_idea(main_idea_id=main_idea.id)
        if not context_chunks:
          logger.error(f"No context chunks found for main idea {main_idea.id} - '{main_idea.main_idea_summary[:30]}...'")
          project_results.append(GenerationResult(
            question_type=generation_request.question_type.value,
            questions=QuestionGenerationResponse(
              signal=ResponseSignal.QUESTION_GENERATION_FAILED.value,
              ideas_processed=0,
              questions_generated=[]
            )
          ))
          break
        
        chunk_ids = [c.chunk_id for c in context_chunks]
        chunks = await chunk_model.get_many_chunks_by_id(chunk_ids=chunk_ids)
        passages = [chunk.chunk_text for chunk in chunks]
        
        generated_q_task = question_controller.generate_questions(
          main_idea_summary=main_idea.main_idea_summary,
          passages=passages,
          question_type=generation_request.question_type,
          num_questions=q_count
        )
        q_tasks.append(generated_q_task)
      
      results = await asyncio.gather(*q_tasks)
      
      questions_generated: List[BaseQuestion] = []
      for result in results:
        questions_generated.extend(result)
              
      project_results.append(GenerationResult(
        question_type=generation_request.question_type.value,
        questions= QuestionGenerationResponse(
          signal=ResponseSignal.QUESTION_GENERATION_SUCCESS.value,
          ideas_processed= len(main_ideas),
          questions_generated= questions_generated
        )
      ))

    overall_results.append(ProjectGenerationResult(
      project_id=project_id,
      results=project_results
    ))


  return BatchQuestionGenerationResponse(
    status_code=status.HTTP_200_OK,
    results=overall_results
  )