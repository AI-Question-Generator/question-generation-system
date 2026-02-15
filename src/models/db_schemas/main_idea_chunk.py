from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from datetime import datetime, timezone


class MainIdeaChunk(BaseModel):
    """
    Represents the association between a MainIdea and a DataChunk.
    Stores metadata about why this chunk is related to the main idea.
    """
    id: Optional[ObjectId] = Field(None, alias="_id")
    main_idea_id: ObjectId
    chunk_id: ObjectId
    similarity_score: float = Field(..., ge=0.0, le=1.0)  # Vector similarity score
    retrieval_rank: int = Field(..., gt=0)  # Rank within top-k results
    embedding_model: str = Field(...)  # Name of embedding model used
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("main_idea_id", 1)],
                "name": "main_idea_id_index_1",
                "unique": False
            },
            {
                "key": [("chunk_id", 1)],
                "name": "chunk_id_index_1",
                "unique": False
            },
            {
                "key": [
                    ("main_idea_id", 1),
                    ("retrieval_rank", 1)
                ],
                "name": "main_idea_id_rank_index_1",
                "unique": False
            }
        ]
