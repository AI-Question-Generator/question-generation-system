from string import Template
from pydantic import BaseModel
from typing import Any

class PromptTemplate(BaseModel):
  system: Template
  user: Template
  response_model: Any