from string import Template
from pydantic import BaseModel
from typing import Any, Union

class PromptTemplate(BaseModel):
  system: Union[Template, str]
  user: Union[Template, str]
  response_model: Any