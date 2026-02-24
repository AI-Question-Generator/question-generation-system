from pydantic import BaseModel, Field

class MainIdea(BaseModel):
    name: str = Field(...)
    summary: str = Field(..., description="Detailed full-sentence summary explaining the concept, its relevance, any examples or applications, its connections to other ideas, and its role in understanding the material.")