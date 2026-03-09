from typing import List, Optional, Union
from bson import ObjectId
from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnum
from .db_schemas import MainIdea
from pymongo import InsertOne, UpdateOne
import logging

class MainIdeaModel(BaseDataModel):
  
  def __init__(self, db_client):
    super().__init__(db_client=db_client)
    self.collection = self.db_client[DataBaseEnum.COLLECTION_MAIN_IDEA_NAME.value]
    self.relation_collection = self.db_client[DataBaseEnum.COLLECTION_MAIN_IDEA_CHUNK_NAME.value]
    self.logger = logging.getLogger(__name__)
  
  @classmethod
  async def create_instance(cls, db_client):
    instance = cls(db_client=db_client)
    await instance.init_collection()
    return instance
  
  async def init_collection(self):
    all_collections = await self.db_client.list_collection_names() 
    
    if DataBaseEnum.COLLECTION_MAIN_IDEA_NAME.value not in all_collections:
    
      self.collection = await self.db_client.create_collection(DataBaseEnum.COLLECTION_MAIN_IDEA_NAME.value)
      
      # Create indexes
      indexes = MainIdea.get_indexes()
    
      for index in indexes:
        await self.collection.create_index(
          index["key"],
          name=index["name"],
          unique=index["unique"]
        )
  
  async def create_main_idea(self, main_idea: MainIdea):
    result = await self.collection.insert_one(main_idea.model_dump(by_alias=True, exclude_unset=True))
    main_idea.id = result.inserted_id
    return main_idea

  async def get_project_main_ideas(self, project_id: Union[str, ObjectId], top: int = 0) -> List[MainIdea]:
    '''Extracts main ideas related to a project'''
    
    query: dict = {
      "main_idea_project_id": ObjectId(project_id) if isinstance(project_id, str) else project_id,
    }
    
    result= await self.collection.find(query).limit(top).to_list(length=None)
    result = [MainIdea(**res) for res in result]
    return result
  
  async def get_project_main_ideas_sample(self, project_id: Union[str, ObjectId], sample_size: int = 10) -> List[MainIdea]:
    '''Extracts a random sample of main ideas related to a project'''
    
    query: dict = {
      "main_idea_project_id": ObjectId(project_id) if isinstance(project_id, str) else project_id,
    }
    
    pipeline = [
      {"$match": query},
      {"$sample": {"size": sample_size}}
    ]
    
    result= await self.collection.aggregate(pipeline).to_list(length=None)
    result = [MainIdea(**res) for res in result]
    return result
  
  async def get_main_idea_record(self, main_idea_id: Union[str, ObjectId]):
    if isinstance(main_idea_id, str):
      main_idea_id = ObjectId(main_idea_id)
      
    record = await self.collection.find_one({'_id': main_idea_id})
    return MainIdea(**record)
  
  async def insert_many_main_ideas(self, main_ideas: list[MainIdea], batch_size: int = 100):
    for i in range(0, len(main_ideas), batch_size):
      batch = main_ideas[i: i+batch_size]
      
      operations = [
        InsertOne(idea.model_dump(by_alias=True, exclude_unset=True))
        for idea in batch
      ]
      
      await self.collection.bulk_write(operations)
      self.logger.info(f"Successfully inserted {len(batch)} ideas batch")
    
    self.logger.info(f"Successfully inserted {len(main_ideas)} ideas")
    return len(main_ideas)

  async def delete_main_idea_by_id(self, main_idea_id: Union[str, ObjectId]):
    if isinstance(main_idea_id, str):
      main_idea_id = ObjectId(main_idea_id)
    
    result = await self.collection.delete_one({'_id': main_idea_id})

    if result.deleted_count == 0:
      self.logger.warning(f"No MainIdea found with id {main_idea_id}")
      return False
    
    self.logger.info(f"Deleted MainIdea of id {main_idea_id}")
    return True
  
  async def delete_many_main_ideas_by_project_id(self, project_id: str):
    result = await self.collection.delete_many({
      "main_idea_project_id": ObjectId(project_id) if isinstance(project_id, str) else project_id
    })
    return result.deleted_count
  
  async def update_many_ranks_by_id(self, main_idea_ids: list[Union[str, ObjectId]], ranks: list[int], batch_size: int = 100):
    if len(main_idea_ids) != len(ranks):
      self.logger.error(f"length of main_idea_ids ({len(main_idea_ids)}) doesn't match ranks ({len(ranks)})")
      return None
    
    for i in range(0, len(main_idea_ids), batch_size):
      batch_main_idea_ids = main_idea_ids[i: i+batch_size]
      batch_ranks = ranks[i: i+batch_size]
      operations = [
        UpdateOne(
          filter={
            '_id': ObjectId(main_idea_id) if isinstance(main_idea_id, str) else main_idea_id
            },
            update={'$set': {'main_idea_rank': rank}}
            )
        for main_idea_id, rank in zip(batch_main_idea_ids, batch_ranks)
      ]
      
      await self.collection.bulk_write(operations)
      self.logger.info(f"Successfully updated {len(batch_ranks)} ranks batch")
    
    self.logger.info(f"Successfully updated {len(ranks)} ranks")
    return len(main_idea_ids)

  async def get_top_idea_chunk_ids(self, main_idea_id: ObjectId, top: int = 0):
    chunk_ids = await self.collection.find({"_id": main_idea_id}, {"main_idea_chunk_ids":1}).limit(top)
    
    if not chunk_ids:
      self.logger.error(f"Main Idea with id {ObjectId} has no chunks")
    
    return chunk_ids
  
  async def update_idea_chunk_ids(self, main_idea_id: Union[str, ObjectId], chunk_ids: List[Union[str, ObjectId]]):
    # Assure that all ids are ObjectIds
    for i, chunk_id in enumerate(chunk_ids):
      if isinstance(chunk_id, str):
        chunk_ids[i] = ObjectId(chunk_id)
    
    result = await self.collection.update_one({'_id': main_idea_id}, {'$set': {'main_idea_chunk_ids': chunk_ids}})
    
    return True
  
  async def count_main_ideas_by_project_id(self, project_id: Union[str, ObjectId]):
    count = await self.collection.count_documents({
      "main_idea_project_id": ObjectId(project_id) if isinstance(project_id, str) else project_id
    })
    return count