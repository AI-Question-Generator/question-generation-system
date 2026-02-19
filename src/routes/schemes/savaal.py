from typing import List, Optional
from pydantic import BaseModel

# Request/Response Models
class MainIdeaExtractionRequest(BaseModel):
    """Request to start main idea extraction pipeline."""
    file_id: str
    chunk_size: int = 100
    section_window_size: int = 3
    top_k_chunks: int = 5


class MainIdeaExtractionResponse(BaseModel):
    """Response from main idea extraction."""
    status: str
    sections_count: int
    candidates_count: int
    consolidated_count: int
    main_ideas_count: int
    chunk_associations_count: int
    message: str


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
