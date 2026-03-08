from typing import List, Union, Optional
from bson import ObjectId
from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnum
from .db_schemas import MainIdeaChunk
from pymongo import InsertOne, UpdateOne
import logging


class MainIdeaChunkModel(BaseDataModel):
  """
  Model for managing MainIdeaChunk associations.
  Handles the relationship between main ideas and document chunks.
  """

  def __init__(self, db_client):
    super().__init__(db_client=db_client)
    self.collection = self.db_client[DataBaseEnum.COLLECTION_MAIN_IDEA_CHUNK_NAME.value]
    self.logger = logging.getLogger(__name__)

  @classmethod
  async def create_instance(cls, db_client):
    instance = cls(db_client=db_client)
    await instance.init_collection()
    return instance

  async def init_collection(self):
    all_collections = await self.db_client.list_collection_names()

    if DataBaseEnum.COLLECTION_MAIN_IDEA_CHUNK_NAME.value not in all_collections:
      self.collection = await self.db_client.create_collection(
        DataBaseEnum.COLLECTION_MAIN_IDEA_CHUNK_NAME.value
      )

      # Create indexes
      indexes = MainIdeaChunk.get_indexes()

      for index in indexes:
        await self.collection.create_index(
        index["key"],
        name=index["name"],
        unique=index.get("unique", False)
        )

  async def insert_many_associations(
    self,
    associations: list[MainIdeaChunk],
    batch_size: int = 100
  ) -> int:
    """
    Bulk insert main idea-chunk associations.
    
    Args:
      associations: List of MainIdeaChunk objects
      batch_size: Number of records per batch
      
    Returns:
      Total number of inserted associations
    """
    for i in range(0, len(associations), batch_size):
      batch = associations[i : i + batch_size]

      operations = [
        InsertOne(assoc.model_dump(by_alias=True, exclude_unset=True))
        for assoc in batch
      ]

      await self.collection.bulk_write(operations)
      self.logger.info(f"Successfully inserted {len(batch)} associations batch")

    self.logger.info(f"Successfully inserted {len(associations)} associations")
    return len(associations)

  async def get_chunks_for_idea(
    self,
    main_idea_id: Union[str, ObjectId],
    limit: int = 0
  ) -> List[MainIdeaChunk]:
    """
    Retrieve all chunks associated with a specific main idea.
    Results are ordered by retrieval rank (ascending).
    
    Args:
      main_idea_id: ID of the main idea
      limit: Maximum number of chunks to return (0 = no limit)
      
    Returns:
      List of MainIdeaChunk associations
    """
    if isinstance(main_idea_id, str):
      main_idea_id = ObjectId(main_idea_id)

    query = {"main_idea_id": main_idea_id}
    cursor = self.collection.find(query).sort("retrieval_rank", 1)
    
    if limit > 0:
      cursor = cursor.limit(limit)
      
    results = await cursor.to_list(length=None)
    return [MainIdeaChunk(**res) for res in results]

  async def delete_by_main_idea_id(self, main_idea_id: Union[str, ObjectId]) -> int:
    """
    Delete all associations for a specific main idea.
    
    Args:
      main_idea_id: ID of the main idea
      
    Returns:
      Number of deleted associations
    """
    if isinstance(main_idea_id, str):
      main_idea_id = ObjectId(main_idea_id)

    result = await self.collection.delete_many({"main_idea_id": main_idea_id})
    self.logger.info(f"Deleted {result.deleted_count} associations for main idea {main_idea_id}")
    return result.deleted_count

  async def delete_by_chunk_id(self, chunk_id: Union[str, ObjectId]) -> int:
    """
    Delete all associations for a specific chunk.
    Useful when cleaning up deleted chunks.
    
    Args:
      chunk_id: ID of the chunk
      
    Returns:
      Number of deleted associations
    """
    if isinstance(chunk_id, str):
      chunk_id = ObjectId(chunk_id)

    result = await self.collection.delete_many({"chunk_id": chunk_id})
    self.logger.info(f"Deleted {result.deleted_count} associations for chunk {chunk_id}")
    return result.deleted_count

  async def get_association(
    self,
    main_idea_id: Union[str, ObjectId],
    chunk_id: Union[str, ObjectId]
  ) -> Optional[MainIdeaChunk]:
    """
    Retrieve a specific association between a main idea and a chunk.
    
    Args:
      main_idea_id: ID of the main idea
      chunk_id: ID of the chunk
      
    Returns:
      MainIdeaChunk object if found, else None
    """
    if isinstance(main_idea_id, str):
      main_idea_id = ObjectId(main_idea_id)
    if isinstance(chunk_id, str):
      chunk_id = ObjectId(chunk_id)

    record = await self.collection.find_one({
      "main_idea_id": main_idea_id,
      "chunk_id": chunk_id
    })
    
    return MainIdeaChunk(**record) if record else None

  async def get_associations_by_project_id(
    self,
    project_id: ObjectId,
  ) -> Optional[List[MainIdeaChunk]]:
    "Retrieve all main idea-chunk associations for a specific project. Useful for project-level analysis or cleanup."
    
    records = await self.collection.find({
    "project_id": project_id
    })
    
    return [MainIdeaChunk(**record) for record in records] if records else None
  
  async def delete_many_associations_by_project_id(
    self,
    project_id: ObjectId,
  ) -> int:
    "Delete all associations for a specific project. Useful when cleaning up deleted projects or resetting."
    
    result = await self.collection.delete_many({
      "project_id": project_id
    })
    
    self.logger.info(f"Deleted {result.deleted_count} associations for project {project_id}")
    
    return result.deleted_count