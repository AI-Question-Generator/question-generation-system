from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator
from stores.llm.templates.locales.LocalesRegistry import SupportedLanguage, get_supported_domains
from bson.objectid import ObjectId
from typing import Optional

class Inspiration(BaseModel):
  id: Optional[ObjectId] = Field(None, alias="_id")
  inspiration_content: str = Field(min_length=1)
  inspiration_language: SupportedLanguage = Field(...)
  inspiration_domain: str = Field(...)
  inspiration_project_id: Optional[ObjectId] = None
  
  model_config = ConfigDict(arbitrary_types_allowed=True, json_encoders={ObjectId: str})

  @model_validator(mode='after')
  def validate_domain(self):
    supported_domains = get_supported_domains(self.inspiration_language)
    if self.inspiration_domain not in supported_domains:
      raise ValueError(
          f"domain '{self.inspiration_domain}' is not supported for language '{self.inspiration_language}'. "
          f"Supported domains: {supported_domains}"
        )
    return self

  @classmethod
  def get_indexes(cls):
    return [
      {
        "key":[("inspiration_language", 1), ("inspiration_domain", 1)],
        "name": "language_domain_index_1",
        "unique": False
      },
      {
        "key":[("inspiration_project_id", 1)],
        "name": "project_id_index_1",
        "unique": False
      }
    ]