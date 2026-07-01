from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from bson.objectid import ObjectId
from typing import Optional
from stores.llm.templates.locales.LocalesRegistry import SupportedLanguage, get_supported_domains
import os

class Project(BaseModel):
  id: Optional[ObjectId] = Field(None, alias="_id")
  project_id: str = Field(..., min_length=1)
  language: SupportedLanguage = Field(...)
  domain: str = Field('')
  
  model_config = ConfigDict(arbitrary_types_allowed=True, json_encoders={ObjectId: str})
  
  ## custom validators
  @field_validator("project_id")
  def validate_project_id(cls, value):
    if not value.replace('-', '').isalnum():
      raise ValueError("project_id must be alphanumeric")
    return value
  
  @model_validator(mode='after')
  def validate_domain(self):
    supported_domains = get_supported_domains(self.language)
    if self.domain and self.domain not in supported_domains:
      raise ValueError(
          f"domain '{self.domain}' is not supported for language '{self.language}'. "
          f"Supported domains: {supported_domains}"
        )
    return self
  
    
  @classmethod
  def get_indexes(cls):
    return [
      {
        "key":[("project_id", 1)],
        "name": "project_id_index_1",
        "unique": True
      }
    ]