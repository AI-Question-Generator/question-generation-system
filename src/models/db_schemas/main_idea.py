from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from bson import ObjectId
from datetime import datetime, timezone

class MainIdea(BaseModel):
  id: Optional[ObjectId] = Field(None, alias="_id")
  idea_project_id: ObjectId
  idea_name: str = Field(..., min_length=1)
  idea_summary: str = Field(..., min_length=1)
  idea_rank: Optional[int] = Field(None, gt=0)
  idea_metadata: Optional[dict] = Field(None)
  pushed_at: datetime = Field(datetime.now(timezone.utc))
  
  model_config = ConfigDict(arbitrary_types_allowed= True)

  @classmethod
  def get_indexes(cls):
    return [
      {
        "key": [("idea_project_id", 1)],
        "name": "idea_project_id_index_1",
        "unique": False
      },
      {
        "key": [
          ("idea_project_id", 1),
          ("idea_rank", 1)
          ],
        "name": "idea_project_id_rank_index_1",
        "unique": True
      }
    ]