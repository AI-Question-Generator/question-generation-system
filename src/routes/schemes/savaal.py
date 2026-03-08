from typing import List, Optional
from pydantic import BaseModel

# Request/Response Models
class MainIdeaExtractionRequest(BaseModel):
  """Request to start main idea extraction pipeline."""
  asset_name: Optional[str] = None
  section_size: int = 2000
  limit: Optional[int] = None
  do_reset: int = 0

class MainIdeaExtractionResponse(BaseModel):
  """Response from main idea extraction."""
  status: str
  sections_count: int
  main_ideas_count: int

class MainIdeaRankRequest(BaseModel):
  """Rank main ideas based on importance"""
  ...

class MainIdeaRankResponse(BaseModel):
  """Response from main ideas ranking"""
  signal: str
  ranked_count: int

class QuestionGenerationRequest(BaseModel):
  """Request to generate questions from main ideas."""
  main_idea_ids: Optional[List[str]] = None  # None = all ideas
  question_types: Optional[List[str]] = None  # ["mcq", "tf", "short_answer"]
  questions_per_idea: int = 2


class QuestionGenerationResponse(BaseModel):
  """Response from question generation."""
  status: str
  ideas_processed: int
  questions_generated: int
  questions_by_type: dict
  message: str


class MainIdeaResponse(BaseModel):
  """Response containing a main idea."""
  id: str
  title: str
  summary: str
  rank: Optional[int]
  chunk_count: Optional[int] = 0


class MainIdeasListResponse(BaseModel):
  """Response containing list of main ideas."""
  project_id: str
  main_ideas_count: int
  main_ideas: List[MainIdeaResponse]


class AssociateChunksRequest(BaseModel):
  """Request to associate chunks to main ideas via vector search."""
  top_k: int = 5
  main_idea_ids: Optional[List[str]] = None  # None = all ideas


class AssociateChunksResponse(BaseModel):
  """Response from chunk association."""
  signal: str
  ideas_processed: int
  total_associations: int
  message: str
