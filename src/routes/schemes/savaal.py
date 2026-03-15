from typing import List, Optional
from pydantic import BaseModel, Field
from models.enums.QuestionEnum import QuestionTypeEnum
from stores.llm.templates.response_models.questions import QuestionType

# Request/Response Models
class MainIdeaExtractionRequest(BaseModel):
  """Request to start main idea extraction pipeline."""
  asset_name: Optional[str] = None
  section_size: int = 2000
  limit: Optional[int] = None
  do_reset: int = 0

class MainIdeaExtractionResponse(BaseModel):
  """Response from main idea extraction."""
  signal: str
  sections_count: int
  main_ideas_count: int

class MainIdeaRankRequest(BaseModel):
  """Rank main ideas based on importance"""
  ...

class MainIdeaRankResponse(BaseModel):
  """Response from main ideas ranking"""
  signal: str
  ranked_count: int



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
  do_reset: int = 0


class AssociateChunksResponse(BaseModel):
  """Response from chunk association."""
  signal: str
  ideas_processed: int
  total_associations: int
  message: str

class QuestionGenerationRequest(BaseModel):
  """Request to generate questions from main ideas."""
  num_questions: int = Field(..., gt=0, description="The number of questions to generate.")
  question_type: QuestionTypeEnum

class QuestionGenerationResponse(BaseModel):
  """Response from question generation."""
  signal: str
  ideas_processed: int
  questions_generated: List[QuestionType]

class ProjectGenerationRequest(BaseModel):
  """A single project's question generation task."""
  project_id: str = Field(..., description="The ID of the project.")
  requests: List[QuestionGenerationRequest] = Field(..., description="A list of question generation requests for the project.")

class BatchQuestionGenerationRequest(BaseModel):
  """The request model for batch question generation."""
  tasks: List[ProjectGenerationRequest] = Field(..., description="A list of generation tasks for multiple projects.")

class GenerationResult(BaseModel):
  """The result of a single question generation request."""
  question_type: str
  questions: QuestionGenerationResponse

class ProjectGenerationResult(BaseModel):
  """The overall result for a single project's generation task."""
  project_id: str
  results: List[GenerationResult]

class BatchQuestionGenerationResponse(BaseModel):
  """The response model for the batch generation endpoint."""
  results: List[ProjectGenerationResult]
