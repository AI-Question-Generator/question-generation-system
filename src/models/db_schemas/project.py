from pydantic import BaseModel, Field, validator, model_validator
from bson.objectid import ObjectId
from typing import Optional
from stores.llm.templates.locales.LocalesRegistry import SupportedLanguage, get_supported_domains
import os

class Project(BaseModel):
  id: Optional[ObjectId] = Field(None, alias="_id")
  project_id: str = Field(..., min_length=1)
  language: SupportedLanguage = Field(...)
  domain: str = Field(...)
  
  
  ## custom validators
  @validator("project_id")
  def validate_project_id(cls, value):
    if not value.isalnum():
      raise ValueError("project_id must be alphanumeric")
    return value
  
  @model_validator(mode='after')
  def validate_domain(self):
    supported_domains = get_supported_domains(self.language)
    if self.domain not in supported_domains:
      raise ValueError(
          f"domain '{self.domain}' is not supported for language '{self.language}'. "
          f"Supported domains: {supported_domains}"
        )
    return self
  
  
  class Config:
    arbitrary_types_allowed = True
    json_encoders = {
      ObjectId: str
    }
    
  @classmethod
  def get_indexes(cls):
    return [
      {
        "key":[("project_id", 1)],
        "name": "project_id_index_1",
        "unique": True
      }
    ]