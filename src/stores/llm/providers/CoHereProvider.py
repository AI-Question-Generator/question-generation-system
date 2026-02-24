from pydantic import BaseModel
from typing import Optional
from ..LLMInterface import LLMInterface, AsyncLLMInterface
from ..LLMEnums import CoHereEnums, DocumentTypeEnum
import cohere
from cohere.types.response_format import JsonObjectResponseFormat
import logging

class CoHereProvider(LLMInterface):
  
  def __init__(self, api_key: str,
                    default_input_max_characters: int = 1000,
                    default_generation_max_output_tokens: int = 1000,
                    default_generation_temperature: float = .5):
    
    self.api_key = api_key
    
    self.default_input_max_characters = default_input_max_characters
    self.default_generation_max_output_tokens = default_generation_max_output_tokens
    self.default_generation_temperature = default_generation_temperature
    
    self.generation_model_id = None
    
    self.embedding_model_id = None
    self.embedding_size = None
    
    self.client = cohere.Client(
      api_key = self.api_key,
    )
    
    self.enums = CoHereEnums
    
    self.logger = logging.getLogger(__name__)

  def set_generation_model(self, model_id: str):
    self.generation_model_id = model_id
  
  
  def set_embedding_model(self, model_id: str, embedding_size: int):
    self.embedding_model_id = model_id
    self.embedding_size = embedding_size
    
  def generate_text(self, prompt: str, chat_history: list =[], max_output_tokens: Optional[int] = None,
                          temperature: Optional[float] = None):
    
    if not self.client:
      self.logger.error("Cohere Client was not set")
      return None
    
    if not self.generation_model_id:
      self.logger.error("Generation Model was not set")
    
    temperature = temperature if temperature else self.default_generation_temperature
    max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
      
    response = self.client.chat(
            model = self.generation_model_id,
            chat_history = chat_history,
            message = prompt,
            temperature = temperature,
            max_tokens = max_output_tokens
        )
    
    if not response or not response.text:
      self.logger.error("ُError While Generation Text Using CoHere") 
      return None
    
    return response.text 
    # return response.message.content[0].text

  def generate_structured_text(
    self,
    prompt: str,
    response_model: type[BaseModel],
    chat_history: list = [],
    max_output_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
  ) -> Optional[str]:
    if not self.client:
      self.logger.error("Cohere Client was not set")
      return None

    if not self.generation_model_id:
      self.logger.error("Generation Model was not set")
      return None

    if not response_model:
      self.logger.error("No response model provided")
      return None

    temperature = temperature if temperature else self.default_generation_temperature
    max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens

    response = self.client.chat(
      model=self.generation_model_id,
      chat_history=chat_history,
      message=prompt,
      temperature=temperature,
      max_tokens=max_output_tokens,
      response_format=JsonObjectResponseFormat(
        schema_=response_model.model_json_schema(),
      ),
    )

    if not response or not response.text:
      self.logger.error("Error while generating structured text using CoHere")
      return None

    return response.text

  def embed_text(self, text: str, document_type: Optional[str] = None) -> Optional[list]:
    if not self.client:
      self.logger.error("CoHere Client was not set")
      return None
    
    if not self.embedding_model_id:
      self.logger.error("Embedding Model for ChoHere was not set")
    
    input_type = CoHereEnums.DOCUMENT
    if input_type == DocumentTypeEnum.QUERY:
      input_type = CoHereEnums.QUERY
      
    response = self.client.embed(
      texts=[text],
      model=self.embedding_model_id,
      # output_dimension=self.embedding_size,
      embedding_types=["float"],
      input_type=input_type
    )  

    if not response or not response.embeddings or not response.embeddings.float:
      self.logger.error("Error While Embedding Text Using CoHere Provider")
      return None
  
    return response.embeddings.float[0]
  

  def construct_prompt(self, prompt: str, role: str):
    return {
      "role":role,
      "text":prompt
    }

class AsyncCoHereProvider(CoHereProvider, AsyncLLMInterface):
  def __init__(self, api_key: str,
                  default_input_max_characters: int = 1000,
                  default_generation_max_output_tokens: int = 1000,
                  default_generation_temperature: float = .5):
  
    self.api_key = api_key
    
    self.default_input_max_characters = default_input_max_characters
    self.default_generation_max_output_tokens = default_generation_max_output_tokens
    self.default_generation_temperature = default_generation_temperature
    
    self.generation_model_id = None
    
    self.embedding_model_id = None
    self.embedding_size = None
    
    self.client = cohere.AsyncClient(
      api_key = self.api_key,
    )
    
    self.enums = CoHereEnums
    
    self.logger = logging.getLogger(__name__)
    
  async def generate_text(self, prompt: str, chat_history: list =[], max_output_tokens: Optional[int] = None,
                          temperature: Optional[float] = None):
    
    if not self.client:
      self.logger.error("Cohere Client was not set")
      return None
    
    if not self.generation_model_id:
      self.logger.error("Generation Model was not set")
    
    temperature = temperature if temperature else self.default_generation_temperature
    max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
      
    response = await self.client.chat(
            model = self.generation_model_id,
            chat_history = chat_history,
            message = prompt,
            temperature = temperature,
            max_tokens = max_output_tokens
        )
    
    if not response or not response.text:
      self.logger.error("Error While Generation Text Using CoHere") 
      return None
    
    return response.text
  
  async def generate_structured_text(
    self,
    prompt: str,
    response_model: type[BaseModel],
    chat_history: list = [],
    max_output_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
  ) -> Optional[str]:
    if not self.client:
      self.logger.error("Cohere Client was not set")
      return None

    if not self.generation_model_id:
      self.logger.error("Generation Model was not set")
      return None

    if not response_model:
      self.logger.error("No response model provided")
      return None

    temperature = temperature if temperature else self.default_generation_temperature
    max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens

    response = await self.client.chat(
      model=self.generation_model_id,
      chat_history=chat_history,
      message=prompt,
      temperature=temperature,
      max_tokens=max_output_tokens,
      response_format=JsonObjectResponseFormat(
        schema_=response_model.model_json_schema(),
      ),
    )

    if not response or not response.text:
      self.logger.error("Error while generating structured text using CoHere")
      return None

    return response.text

  async def embed_text(self, text: str, document_type: Optional[str] = None) -> Optional[list]:
    if not self.client:
      self.logger.error("CoHere Client was not set")
      return None
    
    if not self.embedding_model_id:
      self.logger.error("Embedding Model for ChoHere was not set")
    
    input_type = CoHereEnums.DOCUMENT
    if input_type == DocumentTypeEnum.QUERY:
      input_type = CoHereEnums.QUERY
      
    response = await self.client.embed(
      texts=[text],
      model=self.embedding_model_id,
      embedding_types=["float"],
      input_type=input_type
    )  

    if not response or not response.embeddings or not response.embeddings.float:
      self.logger.error("Error While Embedding Text Using CoHere Provider")
      return None
  
    return response.embeddings.float[0]