import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
  APP_NAME: str
  
  FILE_ALLOWED_TYPES: List[str]
  FILE_ALLOWED_SIZE: int
  
  FILE_DEFAULT_CHUNK_SIZE: int
  
  MONGODB_URL: str
  MONGODB_DATABASE: str
  
  GENERATION_BACKEND: str
  EMBEDDING_BACKEND: str

  OPENAI_API_KEY: Optional[str] = None
  OPENAI_API_URL: Optional[str] = None

  OLLAMA_API_KEY: Optional[str] = None
  OLLAMA_HOST_URL: Optional[str] = None

  COHERE_API_KEY: Optional[str] = None
  GEMINI_API_KEY: Optional[str] = None

  GENERATION_MODEL_ID: Optional[str] = None
  EMBEDDING_MODEL_ID: Optional[str] = None
  EMBEDDING_MODEL_SIZE: Optional[int] = None

  DEFAULT_INPUT_MAX_CHARACHTERS: Optional[int] = None
  GENERATION_DEFAULT_MAX_TOKENS: Optional[int] = None
  GENERATION_DEFAULT_TEMPERATURE: Optional[float] = None
  
  
  VECTOR_DB_BACKEND: str
  VECTOR_DB_PATH: str
  VECTOR_DB_LOCATION: str
  VECTOR_DB_PORT: int
  VECTOR_DB_DISTANCE_METHOD: Optional[str] = None

  PRIMARY_LANG: str 
  DEFAULT_LANG: str
  
  class Config:
    if os.path.exists(".env"):
      env_file = ".env"
    
def get_settings():
  return Settings()