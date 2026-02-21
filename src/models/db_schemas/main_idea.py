from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from datetime import datetime, timezone

class MainIdea(BaseModel):
  id: Optional[ObjectId] = Field(None, alias="_id")
  main_idea_project_id: ObjectId
  main_idea_name: str = Field(..., min_length=1)
  main_idea_summary: str = Field(..., min_length=1)
  main_idea_rank: Optional[int] = Field(None, gt=0)
  main_idea_metadata: Optional[dict] = Field(None)
  main_idea_chunk_ids: Optional[list[ObjectId]] = Field(None)
  created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
  
  model_config = ConfigDict(arbitrary_types_allowed= True)

  @classmethod
  def get_indexes(cls):
    return [
      {
        "key": [("main_idea_project_id", 1)],
        "name": "main_idea_project_id_index_1",
        "unique": False
      },
      {
        "key": [
          ("main_idea_project_id", 1),
          ("main_idea_rank", 1)
          ],
        "name": "main_idea_project_id_rank_index_1",
        "unique": True
      }
    ]