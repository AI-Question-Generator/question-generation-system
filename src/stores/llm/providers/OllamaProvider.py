from typing import Optional
from pydantic import BaseModel
from ..LLMInterface import LLMInterface, AsyncLLMInterface
from ..LLMEnums import OllamaEnums
from ollama import Client, AsyncClient

import logging


class OllamaProvider(LLMInterface):
  
  def __init__(self, api_key: str, api_url: Optional[str] = None,
               default_input_max_characters: int = 1000,
               default_generation_max_output_tokens: int = 1000,
               default_generation_temperature: float = 0.5):
    
    self.api_key = api_key
    self.api_url = api_url
    
    self.default_input_max_characters = default_input_max_characters
    self.default_generation_max_output_tokens = default_generation_max_output_tokens
    self.default_generation_temperature = default_generation_temperature
    
    self.generation_model_id = None
    self.embedding_model_id = None
    self.embedding_size = None
    
    self.client = Client(host=self.api_url)
    self.enums = OllamaEnums
    self.logger = logging.getLogger(__name__)

  
  def set_generation_model(self, model_id: str):
    self.generation_model_id = model_id
  
  
  def set_embedding_model(self, model_id: str, embedding_size: int):
    self.embedding_model_id = model_id
    self.embedding_size = embedding_size
    

  def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: Optional[int] = None,
                    temperature: Optional[float] = None):
    
    if not self.client:
      self.logger.error("Ollama Client was not set")
      return None
  
    if not self.generation_model_id:
      self.logger.error("Generation Model was not set")
      return None
    
    temperature = temperature if temperature else self.default_generation_temperature
    max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
      
    chat_history.append(
      self.construct_prompt(prompt=prompt, role=OllamaEnums.USER.value)
    )
      
    response = self.client.chat(
      model=self.generation_model_id,
      messages=chat_history,
      think=False,
      options={
        "temperature": temperature,
        "num_predict": max_output_tokens
      }
    )
    
    if not response or not response.message:
      self.logger.error("Error while generating text with Ollama")
      return None
    
    return response.message.content
  

  def generate_structured_text(self, prompt: str, response_model: type[BaseModel], chat_history: list = [], 
                               max_output_tokens: Optional[int] = None, temperature: Optional[float] = None):
    if not self.client:
      self.logger.error("Ollama Client was not set")
      return None
  
    if not self.generation_model_id:
      self.logger.error("Generation Model was not set")
      return None
    
    temperature = temperature if temperature else self.default_generation_temperature
    max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
      
    chat_history.append(
      self.construct_prompt(prompt=prompt, role=OllamaEnums.USER.value)
    )
    
    response = self.client.chat(
      model=self.generation_model_id,
      messages=chat_history,
      think=False,
      options={
        "temperature": temperature,
        "num_predict": max_output_tokens
      },
      format=response_model.model_json_schema()
    )
    
    if not response or not response.message:
      self.logger.error("Error while generating structured text with Ollama")
      return None

    return response.message.content
    

  def embed_text(self, text: str, document_type: Optional[str] = None):
    
    if not self.client:
      self.logger.error("Ollama Client was not set")
      return None
    
    if not self.embedding_model_id:
      self.logger.error("Embedding Model was not set")
      return None
    
    response = self.client.embeddings(
      model=self.embedding_model_id,
      prompt=text
    )
    
    if not response or not response.embedding:
      self.logger.error("Error while embedding text with Ollama")
      return None
    
    return response.embedding
  

  def construct_prompt(self, prompt: str, role: str):
    return {
      "role": role,
      "content": prompt
    }


class AsyncOllamaProvider(OllamaProvider, AsyncLLMInterface):
  def __init__(self, api_key: str, api_url: Optional[str] = None,
               default_input_max_characters: int = 1000,
               default_generation_max_output_tokens: int = 1000,
               default_generation_temperature: float = 0.5):
    
    super().__init__(api_key, api_url, default_input_max_characters, 
                     default_generation_max_output_tokens, default_generation_temperature)
    
    self.client = AsyncClient(host=self.api_url)
    self.logger = logging.getLogger(__name__)

  
  async def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: Optional[int] = None,
                          temperature: Optional[float] = None):
    if not self.client:
      self.logger.error("Ollama Client was not set")
      return None
  
    if not self.generation_model_id:
      self.logger.error("Generation Model was not set")
      return None
    
    temperature = temperature if temperature else self.default_generation_temperature
    max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
      
    chat_history.append(
      self.construct_prompt(prompt=prompt, role=OllamaEnums.USER.value)
    )
      
    response = await self.client.chat(
      model=self.generation_model_id,
      messages=chat_history,
      think=False,
      options={
        "temperature": temperature,
        "num_predict": max_output_tokens
      }
    )
    
    if not response or not response.message:
      self.logger.error("Error while generating text with Ollama")
      return None
  
    return response.message.content
  

  async def generate_structured_text(self, prompt: str, response_model: type[BaseModel], chat_history: list = [], 
                                     max_output_tokens: Optional[int] = None, temperature: Optional[float] = None):
    if not self.client:
      self.logger.error("Ollama Client was not set")
      return None
  
    if not self.generation_model_id:
      self.logger.error("Generation Model was not set")
      return None
    
    temperature = temperature if temperature else self.default_generation_temperature
    max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
      
    chat_history.append(
      self.construct_prompt(prompt=prompt, role=OllamaEnums.USER.value)
    )
      
    response = await self.client.chat(
      model=self.generation_model_id,
      messages=chat_history,
      think=False,
      options={
        "temperature": temperature,
        "num_predict": max_output_tokens
      },
      format=response_model.model_json_schema()
    )
    
    if not response or not response.message:
      self.logger.error("Error while generating structured text with Ollama")
      return None
  
    return response.message.content
  

  async def embed_text(self, text: str, document_type: Optional[str] = None):
    if not self.client:
      self.logger.error("Ollama Client was not set")
      return None
    
    if not self.embedding_model_id:
      self.logger.error("Embedding Model was not set")
      return None
      
    response = await self.client.embeddings(
      model=self.embedding_model_id,
      prompt=text
    )
    
    if not response or not response.embedding:
      self.logger.error("Error while embedding text with Ollama")
      return None
    
    return response.embedding