from string import Template
from pydantic import BaseModel, ConfigDict
from typing import Any, Union

class PromptTemplate(BaseModel):
  
  model_config = ConfigDict(arbitrary_types_allowed=True)
  
  system: Union[Template, str]
  user: Union[Template, str]
  response_model: Any