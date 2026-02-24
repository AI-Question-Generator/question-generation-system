from pydantic import BaseModel, Field
from typing import List

class Ranking(BaseModel):
    ranks: List[int] = Field(..., description='Rank corresponding to each idea')