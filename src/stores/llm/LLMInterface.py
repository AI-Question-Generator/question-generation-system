from typing import Optional

from pydantic import BaseModel
from abc import ABC, abstractmethod

class LLMInterface(ABC):
  
  @abstractmethod
  def set_generation_model(self, model_id: str):
    pass
  
  
  @abstractmethod
  def set_embedding_model(self, model_id: str, embedding_size: int):
    pass
  
  @abstractmethod
  def generate_text(self, prompt: str, chat_history: list =[], max_output_tokens: Optional[int] = None, temperature: Optional[float] = None) -> Optional[str]:
    pass

  @abstractmethod
  def generate_structured_text(self, prompt: str, response_model: type[BaseModel], chat_history: list = [], max_output_tokens: Optional[int] = None, temperature: Optional[float] = None, max_retries: Optional[int] = None) -> Optional[str]:
    pass
  
  @abstractmethod
  def embed_text(self, text: str, document_type: Optional[str] = None) -> Optional[list]:
    pass
  
  
  @abstractmethod
  def construct_prompt(self, prompt: str, role: str) -> dict:
    pass
  
class AsyncLLMInterface(LLMInterface):
  
  @abstractmethod
  async def generate_text(self, prompt: str, chat_history: list =[], max_output_tokens: Optional[int] = None, temperature: Optional[float] = None) -> Optional[str]:
    pass

  @abstractmethod
  async def generate_structured_text(self, prompt: str, response_model: type[BaseModel], chat_history: list = [], max_output_tokens: Optional[int] = None, temperature: Optional[float] = None, max_retries: Optional[int] = None) -> Optional[str]:
    pass
  
  @abstractmethod
  async def embed_text(self, text: str, document_type: Optional[str] = None) -> Optional[list]:
    pass