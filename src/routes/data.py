from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal
import os
import aiofiles
import logging

from stores.llm.templates.locales.LocalesRegistry import SupportedLanguage
from .schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemas import DataChunk, Project
from models.AssetModel import AssetModel
from models.db_schemas import Asset
from models.enums import AssetTypeEnum


logger = logging.getLogger('uvicorn.error')


data_router = APIRouter(
  prefix="/data",
  tags=["data"]
)

@data_router.post("/create/{project_id}")
async def create_project(
  request: Request,
  project_id: str,
  language: SupportedLanguage,
  domain: str = "",
  ):
  project_model = await ProjectModel.create_instance(db_client=request.app.state.db_client)

  existing_project = await project_model.get_project(project_id=project_id)
  if existing_project is not None:
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={
        "signal": ResponseSignal.PROJECT_ALREADY_EXISTS.value,
        "project_id": str(existing_project.id),
      }
    )

  try:
    project = await project_model.create_project(
      project=Project(
        project_id=project_id,
        language=language,
        domain=domain,
      )
    )
  except Exception as exc:
    logger.error(f"Error While Creating Project {project_id}: {exc}")
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={
        "signal": ResponseSignal.PROJECT_CREATION_FAILED.value,
      }
    )

  ProjectController().get_project_path(project_id=project_id)

  return JSONResponse(
    content={
      "signal": ResponseSignal.PROJECT_CREATED_SUCCESSFULLY.value,
      "project_id": str(project.id),
    }
  )



@data_router.post("/upload/{project_id}")
async def upload(
  request: Request,
  project_id: str,
  file: UploadFile,
  settings : Settings = Depends(get_settings)
  ):
  project_model = await ProjectModel.create_instance(db_client=request.app.state.db_client)

  project = await project_model.get_project(project_id=project_id)
  if project is None:
    logger.warning(f"Project {project_id} was not found for upload")
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={
        "signal": ResponseSignal.PROJECT_NOT_FOUND.value,
      }
    )

  logger.info(f"Project {project_id} is found with language {project.language} and domain {project.domain}")
  
  # validate file type & validate file size 
  data_controller = DataController()
  
  is_valid, result_signal = data_controller.validate_uploaded_file(file=file)
  
  if not is_valid:
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={
        "signal": result_signal}
    )
    
  # get project path
  project_dir_path = ProjectController().get_project_path(project_id=project_id)
  logger.info(f"Project {project_id} directory path is {project_dir_path}")
  
  file_path, file_id = data_controller.generate_unique_filepath(orig_file_name=file.filename, project_path=project_dir_path)
  logger.info(f"Generated file path for uploaded file {file.filename} is {file_path}")
  
  try:
    
    async with aiofiles.open(file_path, "wb") as f:
      while chunk := await file.read(settings.FILE_DEFAULT_CHUNK_SIZE):
        await f.write(chunk)
        
  except Exception as e:
    
    logger.error(f"Error While Uploading File: {e}")
    
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={
        "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
          }
    )
  
  asset_model = await AssetModel.create_instance(db_client=request.app.state.db_client)    
  asset_resource = Asset( asset_project_id=project.id,
                          asset_type=AssetTypeEnum.FILE.value,
                          asset_name=file_id,
                          asset_size=os.path.getsize(file_path) 
    )
  
  asset_record = await asset_model.create_asset(asset=asset_resource)
  print("here")
  return JSONResponse(
      content={
        "signal": ResponseSignal.FILE_UPLOADED_SUCCESSFULLY.value,
        "file_id": str(asset_record.id),
          }
    )
  
  
@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request,project_id: str, process_request: ProcessRequest):
  
  
  chunk_size=process_request.chunk_size
  overlap_Size=process_request.overlap_size
  do_reset = process_request.do_reset
  
  
  
  project_model = await ProjectModel.create_instance(db_client=request.app.state.db_client)
  project = await project_model.get_project_or_create_one(project_id=project_id)
  
  process_controller = ProcessController(project_id=project_id)
  
  project_files_ids = {}
  
  asset_model = await AssetModel.create_instance(db_client=request.app.state.db_client) 
  
  if process_request.file_id: 
  
    asset_record = await asset_model.get_asset_record(asset_project_id=project.id,
                                                      asset_name=process_request.file_id)
  
    if asset_record is None:
      return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content = {
          "signal" : ResponseSignal.FILE_ID_ERROR.value,
        }
      )
    
    # project_files_ids = { asset_record.id : process_request.file_id }
    project_files_ids = { asset_record.id : asset_record.asset_name }
    
  else:
    
  
    project_files = await asset_model.get_all_project_assets( asset_project_id=project.id,
                                                              asset_type=AssetTypeEnum.FILE.value)
    project_files_ids = {
      record.id : record.asset_name
      for record in project_files
    }
  
  if len(project_files_ids) == 0:
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content = {
        "signal" : ResponseSignal.NO_FILES_IDS.value,
      }
    )
  
  no_records = 0 
  no_files = 0
  
  chunk_model = await ChunkModel.create_instance(db_client=request.app.state.db_client)
  
  if do_reset == 1:
    _ = await chunk_model.delete_chunks_by_project_id(project_id=project.id)
      
    
  
  for asset_id, file_id in project_files_ids.items():
    
    file_content = process_controller.get_file_content(file_id=file_id)
    
    if file_content is None:
      logger.error(f"Error While Processing File ID {file_id}")
      continue
    
    file_chunks = process_controller.process_file_content(file_content=file_content,
                                                    file_id=file_id,
                                                    chunk_size=chunk_size,
                                                    overlap_size=overlap_Size)
    
    if file_chunks is None or len(file_chunks) == 0:
      return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
          "signal":ResponseSignal.CHUNKING_FAILED.value
        }
      )
      
    file_chunks_records = [
      DataChunk(
        chunk_text=chunk.page_content,
        chunk_metadata=chunk.metadata,
        chunk_order= i + 1,
        chunk_project_id=project.id,
        chunk_asset_id=asset_id
        )
      for i,chunk in enumerate(file_chunks)]
    
    
    

    
    no_records += await chunk_model.inserts_many_chunks(chunks=file_chunks_records)
    no_files += 1
  
  return JSONResponse(
    content = {
      "signal" : ResponseSignal.CHUNKING_COMPLETED.value,
      "inserted_chunks": no_records,
      "processed_files" : no_files
    }
  )