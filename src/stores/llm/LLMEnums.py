from enum import Enum

class LLMEnums(Enum):
  
  OPENAI = "OPENAI"
  COHERE = "COHERE"
  GEMINI = "GEMINI"
  OLLAMA = "OLLAMA"

  
class OpenAIEnums(Enum):
  
  SYSTEM = "system"
  ASSISTANT = "assistant"
  USER = "user"

class CoHereEnums(Enum):
  
  SYSTEM = "system"
  ASSISTANT = "assistant"
  USER = "user"
  
  DOCUMENT = "search_document"
  QUERY = "search_query"

class GeminiEnums(Enum):
  SYSTEM = "user"
  USER = "user"
  ASSISTANT = "model"

class OllamaEnums(Enum):
  SYSTEM = "system"
  USER = "user"
  ASSISTANT = "assistant"
  
class DocumentTypeEnum(Enum):
  DOCUMENT = "document"
  QUERY = "query"