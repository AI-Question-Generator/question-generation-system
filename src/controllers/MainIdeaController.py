from .BaseController import BaseController
from typing import List
from stores.llm.templates.template_parser import PromptTemplateParserInterface
import stores.llm.templates.response_models as rm
from stores.llm.LLMInterface import AsyncLLMInterface
from helpers.json_tools import pydantic_model_from_json

import asyncio
import logging
import re

logger = logging.getLogger(__name__)

class MainIdeaController(BaseController):
  '''Controller for extracting, combining, reducing, and ranking main ideas from text sections.'''
  
  # TODO: consider caching the extracted main ideas for each section to avoid redundant LLM calls when combining/reducing/ranking multiple times.
  
  def __init__(
    self,
    generation_client: AsyncLLMInterface,
    embedding_client: AsyncLLMInterface,
    prompt_template_parser: PromptTemplateParserInterface,
    ):
    """
    Initialize MainIdeaController.
    """
    super().__init__()
    self.generation_client = generation_client
    self.embedding_client = embedding_client
    self.prompt_template_parser = prompt_template_parser
    self._extraction_cache = {}  # Cache for extracted ideas
        
    
  async def extract_candidates_from_sections(self, sections: List[str]) -> List[str]:

    # Check cache first
    
    tasks = []
    for section in sections:
      result = self.prompt_template_parser.get(
        "main_idea",
        "extract_prompt",
        {"context": section}
      )
      
      if result is None:
        continue
      
      system_message, user_message, response_model = result
            
      if not system_message or not user_message:
        logger.error("Extraction prompt template not found")
        continue
      
      if not isinstance(user_message, str) or not isinstance(system_message, str):
        logger.error("Invalid prompt template format for main idea extraction")
        continue
      
      chat_history = [
        self.generation_client.construct_prompt(
          prompt=system_message,
          role=self.generation_client.enums.SYSTEM.value,
        )
      ]
      
      task = self.generation_client.generate_text(
        prompt=user_message,
        chat_history=chat_history,
        temperature=0.7
      )
      tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return [result for result in results if result is not None]
  
  async def combine_candidates(self, candidates: list[str]) -> List[rm.MainIdea]:
    
    if not candidates:
      logger.error("No main idea candidates provided to combine")
      return []
    
    context = "\n\n".join(candidates)
    
    result = self.prompt_template_parser.get(
      "main_idea",
      "combine_prompt",
      {"context": context}
    )
    
    if result is None:
      return []
      
    system_message, user_message, response_model = result
      
    if not system_message or not user_message:
      logger.error("Combining prompt template not found")
      return []
    
    if not isinstance(user_message, str) or not isinstance(system_message, str):
      logger.error("Invalid prompt template format for main idea combining")
      return []
    
    chat_history = [
      self.generation_client.construct_prompt(
        prompt=system_message,
        role=self.generation_client.enums.SYSTEM.value,
      )
    ]
    
    response = await self.generation_client.generate_structured_text(
      prompt=user_message,
      chat_history=chat_history,
      response_model=response_model
    )
    try:
      candidates = pydantic_model_from_json(response, response_model)
      return list(candidates) if candidates else []
    except Exception as exc:
      logger.error(f'Main Ideas combining failed in schema validation, Response:\n{response}\n\nException:\n{exc}')
      return []
  
  async def reduce_candidates(self, candidates: List[rm.MainIdea], limit: int) -> List[rm.MainIdea]:
    
    if not candidates:
      logger.error("No main idea candidates provided to combine")
      return []
    
    context = candidates
    
    result = self.prompt_template_parser.get(
      "main_idea",
      "reduce_prompt",
      {"limit": limit, "context": context}
    )
    
    if result is None:
        return []
      
    system_message, user_message, response_model = result
      
    if not system_message or not user_message:
      logger.error("Reducing prompt template not found")
      return []
    
    if not isinstance(user_message, str) or not isinstance(system_message, str):
      logger.error("Invalid prompt template format for main idea reduction")
      return []
        
    chat_history = [
      self.generation_client.construct_prompt(
        prompt=system_message,
        role=self.generation_client.enums.SYSTEM.value,
      )
    ]
    
    response = await self.generation_client.generate_structured_text(
      prompt=user_message,
      chat_history=chat_history,
      response_model=response_model
    )
    
    try:
      candidates = pydantic_model_from_json(response, response_model)
      return list(candidates) if candidates else []
    except Exception as exc:
      logger.error(f'Main Ideas reduction failed in schema validation, Response:\n{response}\n\nException:\n{exc}')
      return []
  

  async def rank_main_ideas(self, ideas: List[rm.MainIdea]) -> List[int]:

    if not ideas:
        return []
    
    context = "\n\n".join([
      f"Main Idea {i}:\n" + idea.summary
      for i, idea in enumerate(ideas, 1)
    ])
    
    result = self.prompt_template_parser.get(
      "main_idea",
      "rank_prompt",
      {"context": context}
    )
    
    if result is None:
        return []
      
    system_message, user_message, response_model = result
    
    if not system_message or not user_message:
      logger.error("Ranking prompt template not found")
      return []
    
    chat_history = [
      self.generation_client.construct_prompt(
        prompt=system_message,
        role=self.generation_client.enums.SYSTEM.value,
      )
    ]
    
    response = await self.generation_client.generate_structured_text(
      prompt=user_message,
      chat_history=chat_history,
      response_model=response_model
    )
    
    try:
      candidates = pydantic_model_from_json(response, response_model)
      return list(candidates) if candidates else []
    except Exception as exc:
      logger.error(f'Main Ideas reranking failed in schema validation, Response:\n{response}\n\nException:\n{exc}')
      return []