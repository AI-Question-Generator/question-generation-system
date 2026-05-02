from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator
from stores.llm.templates.locales.LocalesRegistry import SupportedLanguage, get_supported_domains
from bson.objectid import ObjectId
from typing import Optional

class Inspiration(BaseModel):
  id: Optional[ObjectId] = Field(None, alias="_id")
  content: str = Field(min_length=1)
  language: SupportedLanguage = Field(...)
  domain: str = Field(...)
  project_id: str = Field(..., min_length=1)
  
  model_config = ConfigDict(arbitrary_types_allowed=True, json_encoders={ObjectId: str})
  
  @field_validator("project_id")
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

  @classmethod
  def get_indexes(cls):
    return [
      {
        "key":[("language", 1), ("domain", 1)],
        "name": "language_domain_index_1",
        "unique": False
      },
      {
        "key":[("project_id", 1)],
        "name": "language_domain_index_1",
        "unique": False
      }
    ]