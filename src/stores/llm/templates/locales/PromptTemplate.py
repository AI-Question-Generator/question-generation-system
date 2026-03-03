from string import Template
from pydantic import BaseModel, ConfigDict
from typing import Any

class PromptTemplate(BaseModel):
  
  model_config = ConfigDict(arbitrary_types_allowed=True)
  
  system: Template
  user: Template
  response_model: Any = None