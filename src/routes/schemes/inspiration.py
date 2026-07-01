from pydantic import BaseModel, Field
from typing import Optional, List
from stores.llm.templates.locales.LocalesRegistry import SupportedLanguage

class InspirationExtractionRequest(BaseModel):
    project_id: Optional[str] = Field(None, description="Optional Project ID to bind these inspirations to if we want to save them for a specific project.")
    language: SupportedLanguage = Field(..., description="The language of the template to use.")
    domain: str = Field("", description="The specific educational domain (e.g., english_grammar).")
    text: str = Field(..., description="The source text to extract inspirations from.")
    do_reset: int = 0
    section_size: int = 2000

class InspirationExtractionResponse(BaseModel):
    inspirations: List[str] = Field(..., description="The list of extracted contextual situations.")
    inserted_count: Optional[int] = Field(0, description="The number of inspirations successfully saved to the database.")
