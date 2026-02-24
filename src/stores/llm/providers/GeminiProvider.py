from pydantic import BaseModel
from typing import Optional, Literal, Union, List
from ..LLMInterface import LLMInterface
from ..LLMEnums import GeminiEnums
from google import genai
from google.genai import types
import logging


class GeminiProvider(LLMInterface):
  def __init__(
    self,
    api_key: str,
    api_url: Optional[str] = None,
    default_input_max_characters: int = 1000,
    default_generation_max_output_tokens: int = 1000,
    default_generation_temperature: float = 0.1,
  ):
    self.api_key = api_key
    self.api_url = api_url

    self.default_input_max_characters = default_input_max_characters
    self.default_generation_max_output_tokens = default_generation_max_output_tokens
    self.default_generation_temperature = default_generation_temperature

    self.generation_model_id = None

    self.embedding_model_id = None
    self.embedding_size = None

    self.enums = GeminiEnums
    self.client = genai.Client(
        api_key=self.api_key,
    )

    self.logger = logging.getLogger(__name__)

  def set_generation_model(self, model_id: str):
    self.generation_model_id = model_id

  def set_embedding_model(self, model_id: str, embedding_size: int):
    self.embedding_model_id = model_id
    self.embedding_size = embedding_size

  def process_text(self, text: str):
    return text[: self.default_input_max_characters].strip()

  def generate_text(
    self,
    prompt: str,
    chat_history: list = [],
    max_output_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
  ) -> Optional[str]:
    if not self.client:
      self.logger.error("Gemini client was not set")
      return None

    if not self.generation_model_id:
      self.logger.error("Generation model for Gemini was not set")
      return None

    max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
    temperature = temperature if temperature else self.default_generation_temperature

    chat_history.append(self.construct_prompt(prompt=prompt, role=self.enums.USER.value))

    response = self.client.models.generate_content(
      model=self.generation_model_id,
      contents=chat_history,
      config=types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
      ),
    )

    if (
      not response
      or not response.candidates
      or not response.candidates[0].content
      or not response.candidates[0].content.parts
      or not response.candidates[0].content.parts[0].text
    ):
      self.logger.error("Error while generating text with Gemini")
      return None
    
    return response.candidates[0].content.parts[0].text
  
  def generate_structured_text(
    self,
    prompt: str,
    response_model: type[BaseModel],
    chat_history: list = [],
    max_output_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
  ):
    if not self.client:
      self.logger.error("Gemini client was not set")
      return None

    if not self.generation_model_id:
      self.logger.error("Generation model for Gemini was not set")
      return None

    if not response_model:
      self.logger.error("No response model provided")
      return None
    
    max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
    temperature = temperature if temperature else self.default_generation_temperature

    chat_history.append(self.construct_prompt(prompt=prompt, role=self.enums.USER.value))

    response = self.client.models.generate_content(
      model=self.generation_model_id,
      contents=chat_history,
      config=types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        response_json_schema=response_model.model_json_schema()
      ),
    )

    if (
      not response
      or not response.candidates
      or not response.candidates[0].content
      or not response.candidates[0].content.parts
      or not response.candidates[0].content.parts[0].text
    ):
      self.logger.error("Error while generating structured text with Gemini")
      return None
    
    return response.candidates[0].content.parts[0].text

  def construct_prompt(self, prompt: str, role: str):
    return {"role":role, "parts":[{"text":prompt}]}

  def embed_text(self, text: Union[str, List[str]], document_type: str = None):
    if not self.client:
      self.logger.error("Gemini client was not set")
      return None

    if isinstance(text, str):
      text = [text]
        
    if not self.embedding_model_id:
      self.logger.error("Embedding model for Gemini was not set")
      return None

    response = self.client.models.embed_content(
      model=self.embedding_model_id, contents=text
    )

    if (
      not response
      or not response.embeddings
      or len(response.embeddings) == 0
      or not response.embeddings[0]
    ):
      self.logger.error("Error while embedding text with Gemini")
      return None

    return [embd.values for embd in response.embeddings]
