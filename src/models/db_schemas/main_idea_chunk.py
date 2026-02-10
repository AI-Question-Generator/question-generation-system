from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from bson import ObjectId
from datetime import datetime, timezone


class MainIdeaChunk(BaseModel):
  id: Optional[ObjectId] = Field(None, alias="_id")
  idea_chunk_project_id = ObjectId
  main_idea_id = ObjectId
  chunk_id: ObjectId
  score: float = Field(..., ge=0, le=1)
  retriever: Optional[str] = Field(None, gt=0)
  embedding_model_id: Optional[str] = Field(None, gt=0)
  created_at: datetime = Field(datetime.now(timezone.utc))
  
  model_config = ConfigDict(arbitrary_types_allowed= True)
  
  @classmethod
  def get_indexes(cls):
    return [
      {
        "key":[("idea_chunk_project_id", 1)],
        "name": "idea_chunk_project_id_index_1",
        "unique": False
      },
      {
        "key":[("main_idea_id", 1)],
        "name": "main_idea_id_index_1",
        "unique": False
      },
    ]