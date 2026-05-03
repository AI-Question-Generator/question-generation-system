from typing import List, Optional, Union
from bson import ObjectId
from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnum
from .db_schemas import Inspiration
from pymongo import InsertOne, UpdateOne
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
