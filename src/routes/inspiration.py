from fastapi import APIRouter, Depends, status, Request, Query
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import InspirationController, ProcessController
from models import ResponseSignal
from models.db_schemas import Inspiration
from models.ProjectModel import ProjectModel
from models.InspirationModel import InspirationModel
from stores.llm.templates.template_parser import PromptTemplateParser
from typing import Optional
from bson.objectid import ObjectId
import logging

from .schemes import InspirationExtractionRequest, InspirationExtractionResponse

logger = logging.getLogger("uvicorn.error")


inspiration_router = APIRouter(
  prefix="/api/v1/inspiration", tags=["inspiration"]
)


@inspiration_router.post(
  "/extract",
  response_model=InspirationExtractionResponse,
  status_code=status.HTTP_200_OK,
)
async def extract_inspirations(
  request: Request,
  extraction_request: InspirationExtractionRequest,
  settings: Settings = Depends(get_settings)
):
  """
  Start inspiration extraction pipeline.
  
  Pipeline Steps:
  1. Resolve domain, language, and text sections (from project assets or request payload).
  2. Generate contextual situations (inspirations) for each section in parallel.
  3. Deduplicate the generated inspirations.
  4. Save them to the database.
  """
  project_id = extraction_request.project_id
  
  logger.info(f"Inspiration extraction requested: project={project_id}")

  sections = []
  domain = ""
  language = None

  # 1. Resolve context (project-based or request-based)
  if project_id:
    # Get project
    project_model = await ProjectModel.create_instance(db_client=request.app.state.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)
    domain = project.domain
    language = project.language.value
    
  else:
    # Fallback to request payload for domain, language, and sections
    domain = extraction_request.domain
    language = extraction_request.language.value
  
  # Split text into sections
  process_controller = ProcessController(project_id=project_id or "")
  section_size = extraction_request.section_size
  text = extraction_request.text

  texts = process_controller.process_simpler_splitter(
    texts=[text],
    chunk_size=section_size,
    metadatas=None,
  )
  sections = [doc.page_content for doc in texts]

  # 2. Setup Controller and Parser
  prompt_template_parser = PromptTemplateParser(
    domain=domain,
    language=language,
  )
  
  inspiration_model = await InspirationModel.create_instance(request.app.state.db_client)
  
  inspiration_controller = InspirationController(
    generation_client=request.app.state.generation_client,
    prompt_template_parser=prompt_template_parser,
    inspiration_model=inspiration_model
  )
  
  # 3. Generate Inspirations
  logger.info(f"Generating inspirations from {len(sections)} sections")
  inspirations = await inspiration_controller.generate_inspirations(
    sections=sections,
  )
  logger.info(f"inspirations----> {inspirations}")
  
  if not inspirations:
    logger.warning("No inspirations generated")
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={
        "signal": ResponseSignal.INSPIRATION_EXTRACTION_FAILED.value,
        "sections_count": len(sections),
        "inspirations_count": 0,
      }
    )
  
  # Reset existing inspirations if requested
  if extraction_request.do_reset and project_id:
    logger.info(f"Resetting inspirations for project {project_id}")
    deleted_count = await inspiration_model.delete_many_inspirations_by_project_id(project_id=project.id)
    logger.info(f"Deleted {deleted_count} inspirations for project {project_id}")
  # 4. Save Inspirations
  inspirations = [
    Inspiration(
      inspiration_content=record,
      inspiration_language=language,
      inspiration_domain=domain,
      inspiration_project_id=project.id if project_id else None
    )
    for record in inspirations
  ]
    
  logger.info(f"Saving {len(inspirations)} inspirations to database")
  saved_count = await inspiration_model.insert_many_inspirations(
    inspirations=inspirations,
  )
  
  return JSONResponse(
    status_code=status.HTTP_200_OK,
    content={
        "signal": ResponseSignal.INSPIRATION_EXTRACTION_SUCCESS.value,
        "sections_count": len(sections),
        "inspirations_count": saved_count,
    }
  )