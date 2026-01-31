from .BaseDataModel import BaseDataModel
from .db_schemas import Project
from .enums import DataBaseEnum

class ProjectModel(BaseDataModel):
  def __init__(self, db_client: object):
    super().__init__(db_client=db_client)
    self.collection=self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
    
    
  async def create_project(self, project: Project):
    result = await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))
    project._id = result.inserted_id
    return project
  
  
    
  async def get_project_or_create_one(self, project_id: str):
    record = await self.collection.find_one({"project_id":project_id})
    
    # create new project if not found
    if record is None:
      project = Project(project_id=project_id)
      project = await self.create_project(project=project)
      return project
    
    return Project(**record)
  
  
  async def get_all_projects(self, page: int= 1, page_size: int = 10):
    
    # calculate total documents
    total_documents = await self.collection.count_documents({})
    
    # calculate total pages
    total_pages = total_documents // page_size
    
    if total_documents % page_size != 0:
      total_pages += 1
      
      
    # for pagination
    cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size)
    
    # fetch all projects
    projects = []
    
    async for document in cursor:
      projects.append(Project(**document))
      
    return projects, total_pages    