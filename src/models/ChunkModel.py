from .BaseDataModel import BaseDataModel
from .db_schemas import DataChunk, MainIdea
from .enums import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne
from typing import Optional, List, Union
import logging


class ChunkModel(BaseDataModel):
  def __init__(self, db_client: object):
    super().__init__(db_client=db_client)
    self.collection=self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
    self.logger = logging.getLogger(__name__)
    
  @classmethod
  async def create_instance(cls, db_client: object):
    instance = cls(db_client=db_client)
    await instance.init_collection()
    return instance
    
  async def init_collection(self):
    all_collections = await self.db_client.list_collection_names()
    if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collections:
      self.collection = await self.db_client.create_collection(DataBaseEnum.COLLECTION_CHUNK_NAME.value)
      # create indexes
      indexes = DataChunk.get_indexes()
    
      for index in indexes:
        await self.collection.create_index(
          index["key"],
          name=index["name"],
          unique=index["unique"]
        ) 
  
  async def create_chunk(self, chunk: DataChunk):
    result = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))
    chunk.id = result.inserted_id
    return chunk
    
  async def get_chunk(self, chunk_id: str):
    record = await self.collection.find_one({
      "_id": ObjectId(chunk_id)
    })
    
    if record is None:
      return None
    
    return DataChunk(**record)
  
  async def get_many_chunks_by_id(self, chunk_ids: List[Union[str, ObjectId]]):
    # Validate chunk_ids are ObjectIds
    for idx, chunk_id in enumerate(chunk_ids):
      if isinstance(chunk_id, str):
        chunk_ids[idx] = ObjectId(chunk_id)
    
    # Get results
    result = await self.db_client.find({"_id": {"$in": chunk_ids}})
    chunks = [ChunkModel(**res) for res in result]
    self.logger.info(f"Retrieved {len(chunks)} chunks by id")
    return chunks
  
  async def inserts_many_chunks(self, chunks: list, batch_size: int = 100):
    
    for i in range(0, len(chunks), batch_size):
      batch = chunks[i:i + batch_size]
      
      operations = [
        InsertOne(chunk.dict(by_alias=True, exclude_unset=True))
        for chunk in batch
      ]
      
      await self.collection.bulk_write(operations)
      
    return len(chunks)
  
  async def delete_chunks_by_project_id(self, project_id: ObjectId):
    result = await self.collection.delete_many({
      "chunk_project_id": project_id
    })
    return result.deleted_count
  
  
  async def get_project_chunks(self, project_id: ObjectId, page_no: int = 1, page_size: int = 50):
    records = await self.collection.find({
      "chunk_project_id": project_id
    }).skip(
      (page_no - 1) * page_size
    ).limit(page_size).to_list(length=None)
    
    chunks = [
      DataChunk(**rec)
      for rec in records
    ]
    
    return chunks
  
  
  
  async def get_chunks_by_asset_id(self, asset_id: ObjectId) -> List[DataChunk]:
    records = await self.collection.find({
      "chunk_asset_id": asset_id
    }).sort("chunk_order", 1).to_list(length=None)
    
    chunks = [
      DataChunk(**rec)
      for rec in records
    ]
    
    return chunks