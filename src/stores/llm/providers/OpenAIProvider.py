from typing import Optional
from pydantic import BaseModel
from ..LLMInterface import LLMInterface, AsyncLLMInterface
from ..LLMEnums import OpenAIEnums
from openai import OpenAI, AsyncOpenAI
from helpers.json_tools import pydantic_model_from_json

import logging


class OpenAIProvider(LLMInterface):
  
  def __init__(self, api_key: str, api_url: Optional[str] = None,
                    default_input_max_characters: int = 1000,
                    default_generation_max_output_tokens: int = 1000,
                    default_generation_temperature: float = .5,
                    max_retries: int = 0):
    
    self.api_key = api_key
    self.api_url = api_url
    
    self.default_input_max_characters = default_input_max_characters
    self.default_generation_max_output_tokens = default_generation_max_output_tokens
    self.default_generation_temperature = default_generation_temperature
    self.max_retries = max_retries
    
    self.generation_model_id = None
    
    self.embedding_model_id = None
    self.embedding_size = None
    
    self.client = OpenAI(
      api_key = self.api_key,
      base_url = self.api_url
    )
    
    self.enums = OpenAIEnums
    
    self.logger = logging.getLogger(__name__)

  
  def set_generation_model(self, model_id: str):
    self.generation_model_id = model_id
  
  
  def set_embedding_model(self, model_id: str, embedding_size: int):
    self.embedding_model_id = model_id
    self.embedding_size = embedding_size
    
  def generate_text(self, prompt: str, chat_history: list =[], max_output_tokens: Optional[int] = None,
                          temperature: Optional[float] = None):
    
    if not self.client:
      self.logger.error("OpenAI Client was not set")
      return None
  
    if not self.generation_model_id:
      self.logger.error("Generation Model was not set")
      return None
    
    temperature = temperature if temperature else self.default_generation_temperature
    max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
      
    chat_history.append(
      self.construct_prompt(prompt=prompt,role=OpenAIEnums.USER.value)
    )
      
    response = self.client.chat.completions.create(
                          model=self.generation_model_id,
                          messages=chat_history,
                          max_tokens=max_output_tokens,
                          temperature=temperature,
                          extra_body={"chat_template_kwargs": {"enable_thinking": False}}
                          )
    
    if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
      self.logger.error("Error while Generation Text with OpenAI")
      return None
    
    return response.choices[0].message.content
  
  def generate_structured_text(self, prompt: str, response_model: type[BaseModel], chat_history: list = [], max_output_tokens: Optional[int] = None, temperature: Optional[float] = None):
    if not self.client:
      self.logger.error("OpenAI Client was not set")
      return None
  
    if not self.generation_model_id:
      self.logger.error("Generation Model was not set")
      return None
    
    temperature = temperature if temperature else self.default_generation_temperature
    max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
      
    chat_history.append(
      self.construct_prompt(prompt=prompt,role=OpenAIEnums.USER.value)
    )
    
    for attempt in range(self.max_retries + 1):
      try:
        response = self.client.chat.completions.create(
                          model=self.generation_model_id,
                          messages=chat_history,
                          max_tokens=max_output_tokens,
                          temperature=temperature,
                          reasoning_effort=None,
                          response_format={
                            "type": "json_schema",
                            "json_schema": {
                              "name": "structured_response",
                              "schema": response_model.model_json_schema(),
                            },
                          },
                          extra_body={"chat_template_kwargs": {"enable_thinking": False}}
                          )
      
        pydantic_model_from_json(response.choices[0].message.content, model_class=response_model)
      except Exception as exc:
        self.logger.error(f'Error on attempt {attempt}\nError:\n{exc}\n\nretrying...')
        chat_history.append(self.construct_prompt(prompt=f'{exc}', role=OpenAIEnums.USER.value))
    
    
    if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
      self.logger.error("Error while Generating Structured Text with OpenAI")
      return None

    return response.choices[0].message.content
    
  def embed_text(self, text: str, document_type: Optional[str] = None):
    
    if not self.client:
      self.logger.error("OpenAI Client was not set")
      return None
    
    if not self.embedding_model_id:
      self.logger.error("Embedding Model was not set")
      return None
    
    response = self.client.embeddings.create(
                            input=text,
                            model=self.embedding_model_id)
    
    if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding :
      self.logger.error("Error while Embedding Text with OpenAI")
      return None
    
    return response.data[0].embedding
  
  def construct_prompt(self, prompt: str, role: str):
    return {
      "role":role,
      "content":prompt
    }

class AsyncOpenAIProvider(OpenAIProvider, AsyncLLMInterface):
  def __init__(self, api_key: str, api_url: Optional[str] = None,
                    default_input_max_characters: int = 1000,
                    default_generation_max_output_tokens: int = 1000,
                    default_generation_temperature: float = .5,
                    max_retries: int = 0):
    self.api_key = api_key
    self.api_url = api_url
    
    self.default_input_max_characters = default_input_max_characters
    self.default_generation_max_output_tokens = default_generation_max_output_tokens
    self.default_generation_temperature = default_generation_temperature
    self.max_retries = max_retries
    
    self.generation_model_id = None
    
    self.embedding_model_id = None
    self.embedding_size = None
    
    self.client = AsyncOpenAI(
      api_key = self.api_key,
      base_url = self.api_url
    )
    
    self.enums = OpenAIEnums
    
    self.logger = logging.getLogger(__name__)
  
  async def generate_text(self, prompt: str, chat_history: list =[], max_output_tokens: Optional[int] = None,
                          temperature: Optional[float] = None):
    if not self.client:
      self.logger.error("OpenAI Client was not set")
      return None
  
    if not self.generation_model_id:
      self.logger.error("Generation Model was not set")
      return None
    
    temperature = temperature if temperature else self.default_generation_temperature
    max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
      
    chat_history.append(
      self.construct_prompt(prompt=prompt,role=OpenAIEnums.USER.value)
    )
      
    response = await self.client.chat.completions.create(
                          model=self.generation_model_id,
                          messages=chat_history,
                          max_tokens=max_output_tokens,
                          temperature=temperature,
                          )
    
    if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
      self.logger.error("Error while Generating Structured Text with OpenAI")
      return None
  
    return response.choices[0].message.content
  
  async def generate_structured_text(self, prompt: str, response_model: type[BaseModel], chat_history: list = [], max_output_tokens: Optional[int] = None, temperature: Optional[float] = None):
    if not self.client:
      self.logger.error("OpenAI Client was not set")
      return None
  
    if not self.generation_model_id:
      self.logger.error("Generation Model was not set")
      return None
    
    temperature = temperature if temperature else self.default_generation_temperature
    max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
      
    chat_history.append(
      self.construct_prompt(prompt=prompt,role=OpenAIEnums.USER.value)
    )
    
    for attempt in range(self.max_retries + 1):
      try:
        response = await self.client.chat.completions.create(
                      model=self.generation_model_id,
                      messages=chat_history,
                      max_tokens=max_output_tokens,
                      temperature=temperature,
                      reasoning_effort=None,
                      response_format={
                        "type": "json_schema",
                        "json_schema": {
                          "name": "structured_response",
                          "schema": response_model.model_json_schema(),
                        },
                      }
                      )
      
        pydantic_model_from_json(response.choices[0].message.content, model_class=response_model)
      except Exception as exc:
        self.logger.error(f'Error on attempt {attempt}\nError:\n{exc}\n\nretrying...')

        chat_history.append(self.construct_prompt(prompt=f'{exc}', role=OpenAIEnums.USER.value))
    
    if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
      self.logger.error("Error while Generating Structured Text with OpenAI")
      return None
  
    return response.choices[0].message.content
  
  async def embed_text(self, text: str, document_type: Optional[str] = None):

    if not self.client:
      self.logger.error("OpenAI Client was not set")
      return None
    
    if not self.embedding_model_id:
      self.logger.error("Embedding Model was not set")
      return None
      
    response = await self.client.embeddings.create(
                  input=text,
                  model=self.embedding_model_id
                  )
    
    if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding :
      self.logger.error("Error while Embedding Text with OpenAI")
      return None
    
    return response.data[0].embedding