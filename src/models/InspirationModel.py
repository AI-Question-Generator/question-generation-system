from typing import List, Optional, Union
from bson import ObjectId
from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnum
from .db_schemas import Inspiration
from pymongo import InsertOne
from stores.llm.templates.locales.LocalesRegistry import SupportedLanguage
import logging

class InspirationModel(BaseDataModel):
  
  def __init__(self, db_client):
    super().__init__(db_client=db_client)
    self.collection = self.db_client[DataBaseEnum.COLLECTION_INSPIRATION_NAME.value]
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

  async def get_project_inspirations(
      self, 
      language: SupportedLanguage, 
      domain: str, 
      project_id: Optional[Union[str, ObjectId]], 
      top: int = 0, 
      exclude_project_unset: bool = False
  ) -> List[Inspiration]:
    '''Extracts inspirations related to a project'''
    
    project_id_obj = ObjectId(project_id) if isinstance(project_id, str) else project_id
    
    query: dict = {
      "inspiration_language": language,
      "inspiration_domain": domain,
    }
    
    if project_id_obj is not None:
      if not exclude_project_unset:
        query['$or'] = [
          {"inspiration_project_id": project_id_obj},
          {"inspiration_project_id": None}
        ]
      else:
        query["inspiration_project_id"] = project_id_obj
    else:
      query["inspiration_project_id"] = None
    
    result = await self.collection.find(query).limit(top).to_list(length=None)
    result = [Inspiration(**res) for res in result]
    return result
  
  async def get_inspiration_sample(
      self, 
      language: SupportedLanguage, 
      domain: str, 
      sample_size: int = 1, 
      exclude_project_set: bool = False
  ) -> List[Inspiration]:
    '''Extracts inspirations related to a language and a domain'''
    
    query: dict = {
      "inspiration_language": language,
      "inspiration_domain": domain,
    }
    
    if exclude_project_set:
      query["inspiration_project_id"] = None
    
    pipeline = [
      {"$match": query},
      {"$sample": {"size": sample_size}}
    ]
    
    result = await self.collection.aggregate(pipeline)
    result = await result.to_list(length=None)
    result = [Inspiration(**res) for res in result]
    return result
    
  async def get_project_inspiration_sample(
      self, 
      language: SupportedLanguage, 
      domain: str, 
      project_id: Optional[Union[str, ObjectId]], 
      sample_size: int = 1, 
      exclude_project_unset: bool = False
  ) -> List[Inspiration]:
    '''Extracts inspirations related to a project'''
    
    project_id_obj = ObjectId(project_id) if isinstance(project_id, str) else project_id
    
    query: dict = {
      "inspiration_language": language,
      "inspiration_domain": domain,
    }
    
    if project_id_obj is not None:
      if not exclude_project_unset:
        query['$or'] = [
          {"inspiration_project_id": project_id_obj},
          {"inspiration_project_id": None}
        ]
      else:
        query["inspiration_project_id"] = project_id_obj
    else:
      query["inspiration_project_id"] = None
    
    pipeline = [
      {"$match": query},
      {"$sample": {"size": sample_size}}
    ]
    
    result = await self.collection.aggregate(pipeline)
    result = await result.to_list(length=None)
    result = [Inspiration(**res) for res in result]
    return result

  async def get_inspiration_record(self, inspiration_id: Union[str, ObjectId]) -> Optional[Inspiration]:
    if isinstance(inspiration_id, str):
      inspiration_id = ObjectId(inspiration_id)
      
    record = await self.collection.find_one({'_id': inspiration_id})
    return Inspiration(**record) if record else None

  async def insert_many_inspirations(self, inspirations: List[Inspiration], batch_size: int = 100) -> int:
    for i in range(0, len(inspirations), batch_size):
      batch = inspirations[i: i+batch_size]
      
      operations = [
        InsertOne(insp.model_dump(by_alias=True, exclude_unset=True))
        for insp in batch
      ]
      
      await self.collection.bulk_write(operations)
      self.logger.info(f"Successfully inserted {len(batch)} inspirations batch")
    
    self.logger.info(f"Successfully inserted {len(inspirations)} inspirations")
    return len(inspirations)

  async def delete_inspiration_by_id(self, inspiration_id: Union[str, ObjectId]) -> bool:
    if isinstance(inspiration_id, str):
      inspiration_id = ObjectId(inspiration_id)
    
    result = await self.collection.delete_one({'_id': inspiration_id})

    if result.deleted_count == 0:
      self.logger.warning(f"No Inspiration found with id {inspiration_id}")
      return False
    
    self.logger.info(f"Deleted Inspiration of id {inspiration_id}")
    return True
  
  async def delete_many_inspirations_by_project_id(self, project_id: Union[str, ObjectId]) -> int:
    project_id_obj = ObjectId(project_id) if isinstance(project_id, str) else project_id
    result = await self.collection.delete_many({
      "inspiration_project_id": project_id_obj
    })
    return result.deleted_count

  async def count_inspirations_by_project_id(self, project_id: Union[str, ObjectId]) -> int:
    project_id_obj = ObjectId(project_id) if isinstance(project_id, str) else project_id
    count = await self.collection.count_documents({
      "inspiration_project_id": project_id_obj
    })
    return count
