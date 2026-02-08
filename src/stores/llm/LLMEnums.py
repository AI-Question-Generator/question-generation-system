from enum import Enum

class LLMEnums(Enum):
  
  OPENAI = "OPENAI"
  COHERE = "COHERE"
  GEMINI = "GEMINI"

  
class OpenAIEnums(Enum):
  
  SYSTEM = "system"
  ASSISTANT = "assistant"
  USER = "user"

class CoHereEnums(Enum):
  
  SYSTEM = "SYSTEM"
  ASSISTANT = "CHATBOT"
  USER = "USER"
  
  DOCUMENT = "search_document"
  QUERY = "search_query"

class GeminiEnums(Enum):
  SYSTEM = "user"
  USER = "user"
  ASSISTANT = "model"

class DocumentTypeEnum(Enum):
  DOCUMENT = "document"
  QUERY = "query"