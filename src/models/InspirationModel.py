from typing import List, Optional, Union
from bson import ObjectId
from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnum
from .db_schemas import Inspiration
from pymongo import InsertOne, UpdateOne
from stores.llm.templates.locales.LocalesRegistry import SupportedLanguage
import logging

class InspirationModel(BaseDataModel):
  
  def __init__(self, db_client):
    super().__init__(db_client=db_client)
    self.collection = self.db_client[DataBaseEnum.COLLECTION_INSPIRATION_NAME.value]
    self.relation_collection = self.db_client[DataBaseEnum.COLLECTION_MAIN_IDEA_CHUNK_NAME.value]
    self.logger = logging.getLogger(__name__)
  
  @classmethod
  async def create_instance(cls, db_client):
    instance = cls(db_client=db_client)
    await instance.init_collection()
    return instance
  
  async def init_collection(self):
    all_collections = await self.db_client.list_collection_names() 
    
    if DataBaseEnum.COLLECTION_INSPIRATION_NAME.value not in all_collections:
    
      self.collection = await self.db_client.create_collection(DataBaseEnum.COLLECTION_INSPIRATION_NAME.value)
      
      # Create indexes
      indexes = Inspiration.get_indexes()
    
      for index in indexes:
        await self.collection.create_index(
          index["key"],
          name=index["name"],
          unique=index["unique"]
        )

  async def create_inspiration(self, inspiration: Inspiration):
    result = await self.collection.insert_one(inspiration.model_dump(by_alias=True, exclude_unset=True))
    inspiration.id = result.inserted_id
    return inspiration

  async def get_project_inspirations(self, language: SupportedLanguage, domain: str, project_id: Optional[Union[str, ObjectId]], top: int = 0, exclude_project_unset: bool = False) -> List[Inspiration]:
    '''Extracts inspirations related to a project'''
    
    query: dict = {
      "inspiration_language": language,
      "inspiration_domain": domain,
      '$or': [
        {"inspiration_project_id": ObjectId(project_id) if isinstance(project_id, str) else project_id}
      ]
    }
    
    if not exclude_project_unset:
      query['$or'].append({"inspiration_project_id": None})
    
    
    result= await self.collection.find(query).limit(top).to_list(length=None)
    result = [Inspiration(**res) for res in result]
    return result