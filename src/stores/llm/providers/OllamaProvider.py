from typing import Optional
from pydantic import BaseModel
from ..LLMInterface import LLMInterface, AsyncLLMInterface
from ..LLMEnums import OllamaEnums
from ollama import Client, AsyncClient
from helpers.json_tools import pydantic_model_from_json
from helpers.semaphore import with_gen_semaphore

import logging


class OllamaProvider(LLMInterface):
  
  def __init__(self, api_key: str, api_url: Optional[str] = None,
               default_input_max_characters: int = 1000,
               default_generation_max_output_tokens: int = 1000,
               default_generation_temperature: float = 0.5,
               default_max_retries: int = 0):
    
    self.api_key = api_key
    self.api_url = api_url
    
    self.default_input_max_characters = default_input_max_characters
    self.default_generation_max_output_tokens = default_generation_max_output_tokens
    self.default_generation_temperature = default_generation_temperature
    self.default_max_retries = default_max_retries
    
    self.generation_model_id = None
    self.embedding_model_id = None
    self.embedding_size = None
    
    self.enums = OllamaEnums
    self.client = Client(host=self.api_url)
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
      self.construct_prompt(prompt=prompt, role=self.enums.USER.value)
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
                               max_output_tokens: Optional[int] = None, temperature: Optional[float] = None, max_retries: Optional[int] = None):
    if not self.client:
      self.logger.error("Ollama Client was not set")
      return None
  
    if not self.generation_model_id:
      self.logger.error("Generation Model was not set")
      return None
    
    if max_retries is None:
      max_retries = self.default_max_retries

    temperature = temperature if temperature else self.default_generation_temperature
    max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
      
    chat_history.append(
      self.construct_prompt(prompt=prompt, role=self.enums.USER.value)
    )
    
    for attempt in range(max_retries + 1):
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

      try:
        pydantic_model_from_json(response.message.content, model_class=response_model)
      except Exception as exc:
        self.logger.error(f'Error on attempt {attempt}\nError:\n{exc}')
        if attempt != max_retries:
          self.logger.error('\nretrying...')
          chat_history.append(self.construct_prompt(prompt=response.message.content, role=self.enums.ASSISTANT.value))
          chat_history.append(self.construct_prompt(prompt=f'{exc}', role=self.enums.USER.value))

    if not response or not response.message or not response.message.content:
      self.logger.error("Error while generating structured text with Ollama")
      return None
    
    return response.message.content
    

  def embed_text(self, text: str, document_type: Optional[str] = None) -> Optional[list]:
    
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
               default_generation_temperature: float = 0.5,
               default_max_retries: int = 0):
    
        
    self.api_key = api_key
    self.api_url = api_url
    
    self.default_input_max_characters = default_input_max_characters
    self.default_generation_max_output_tokens = default_generation_max_output_tokens
    self.default_generation_temperature = default_generation_temperature
    self.default_max_retries = default_max_retries
    
    self.generation_model_id = None
    self.embedding_model_id = None
    self.embedding_size = None
    
    self.enums = OllamaEnums
    
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
      self.construct_prompt(prompt=prompt, role=self.enums.USER.value)
    )
      
    response = await with_gen_semaphore(self.client.chat(
      model=self.generation_model_id,
      messages=chat_history,
      think=False,
      options={
        "temperature": temperature,
        "num_predict": max_output_tokens
      }
    ))
    
    if not response or not response.message:
      self.logger.error("Error while generating text with Ollama")
      return None
  
    return response.message.content
  

  async def generate_structured_text(self, prompt: str, response_model: type[BaseModel], chat_history: list = [], 
                                     max_output_tokens: Optional[int] = None, temperature: Optional[float] = None, max_retries: Optional[int] = None):
    if not self.client:
      self.logger.error("Ollama Client was not set")
      return None
  
    if not self.generation_model_id:
      self.logger.error("Generation Model was not set")
      return None
    
    if max_retries is None:
      max_retries = self.default_max_retries

    temperature = temperature if temperature else self.default_generation_temperature
    max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
      
    chat_history.append(
      self.construct_prompt(prompt=prompt, role=self.enums.USER.value)
    )
    
    for attempt in range(max_retries + 1):
      response = await with_gen_semaphore(self.client.chat(
        model=self.generation_model_id,
        messages=chat_history,
        think=False,
        options={
          "temperature": temperature,
          "num_predict": max_output_tokens
        },
        format=response_model.model_json_schema()
      ))

      try:
        pydantic_model_from_json(response.message.content, model_class=response_model)
      except Exception as exc:
        self.logger.error(f'Error on attempt {attempt}\nError:\n{exc}\n\nretrying...')
        if attempt != max_retries:
          chat_history.append(self.construct_prompt(prompt=response.message.content, role=self.enums.ASSISTANT.value))
          chat_history.append(self.construct_prompt(prompt=f'{exc}', role=self.enums.USER.value))

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