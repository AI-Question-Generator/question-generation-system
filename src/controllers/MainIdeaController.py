from asyncio import tasks
from .BaseController import BaseController
from models.db_schemas import MainIdea
from typing import List, Dict, Tuple
from models.MainIdeaModel import MainIdeaModel
from bson.objectid import ObjectId
from datetime import datetime, timezone
from stores.llm.templates.template_parser import PromptTemplateParserInterface
import stores.llm.templates.response_models as rm
from stores.llm.LLMInterface import LLMInterface
from stores.vectordb.VectorDBInterface import VectorDBInterface
import asyncio
import logging
import re

logger = logging.getLogger(__name__)

class MainIdeaController(BaseController):
  '''Controller for extracting, combining, reducing, and ranking main ideas from text sections.'''
  
  # TODO: consider supporting async calls to the generation & embedding client for better performance.
  # TODO: consider caching the extracted main ideas for each section to avoid redundant LLM calls when combining/reducing/ranking multiple times.
  
  def __init__(
    self,
    generation_client: LLMInterface,
    embedding_client: LLMInterface,
    prompt_template_parser: PromptTemplateParserInterface,
    project_id
    ):
    """
    Initialize MainIdeaController.
    """
    super().__init__()
    self.generation_client = generation_client
    self.embedding_client = embedding_client
    self.prompt_template_parser = prompt_template_parser
    self.project_id = project_id
        
    
  async def extract_candidates_from_sections(self, sections: List[str]) -> List[rm.MainIdea]:
      
    results = []
    for section in sections:
      prompt = self.prompt_template_parser.get(
        "main_idea",
        "extraction_prompt",
        {"context": section}
      )
      
      if not prompt:
        logger.error("Extraction prompt template not found")
        return []
      
      if not isinstance(prompt.user, str) or not isinstance(prompt.system, str):
        logger.error("Invalid prompt template format for main idea extraction")
        return []
      
      chat_history = [
        self.generation_client.construct_prompt(
          prompt=prompt.system,
          role=self.generation_client.enums.SYSTEM.value,
        )
      ]
      
      response = self.generation_client.generate_structured_text(prompt=prompt.user, chat_history=chat_history, response_model=prompt.response_model)
      results.append(response)
        
    main_ideas_list = []
    for res in results:
      if isinstance(res, BaseException):
        logger.error(f"Exception occured when extracting idea from section: {res}")
        continue
      
      res = prompt.response_model.model_validate_json(res)
      main_ideas_list += list(res)
      
    return main_ideas_list

  
  async def combine_candidates(self, candidates: List[rm.MainIdea]) -> List[rm.MainIdea]:
    
    if not candidates:
      logger.error("No main idea candidates provided to combine")
      return []
    
    context = "\n".join([
      candidate.summary
      for candidate in candidates
    ])
    
    prompt = self.prompt_template_parser.get(
        "main_idea",
        "combining_prompt",
        {"context": context}
    )
    
    if not prompt:
      logger.error("Reducing prompt template not found")
      return []
    
    if not isinstance(prompt.user, str) or not isinstance(prompt.system, str):
        logger.error("Invalid prompt template format for main idea combining")
        return []
    
    chat_history = [
      self.generation_client.construct_prompt(
        prompt=prompt.system,
        role=self.generation_client.enums.SYSTEM.value,
      )
    ]
    
    response = self.generation_client.generate_structured_text(
      prompt=prompt.user,
      chat_history=chat_history,
      response_model=prompt.response_model,
    )
    
    return list(prompt.response_model.model_validate_json(response)) if response else []
  
  async def reduce_candidates(self, candidates: List[rm.MainIdea]) -> List[rm.MainIdea]:
    
    if not candidates:
      logger.error("No main idea candidates provided to combine")
      return []
    
    context = "\n".join([
      candidate.summary
      for candidate in candidates
    ])
    
    prompt = self.prompt_template_parser.get(
        "main_idea",
        "combining_prompt",
        {"context": context}
    )
    
    if not prompt:
      logger.error("Reducing prompt template not found")
      return []
    
    if not isinstance(prompt.user, str) or not isinstance(prompt.system, str):
      logger.error("Invalid prompt template format for main idea reduction")
      return []
      
    chat_history = [
      self.generation_client.construct_prompt(
        prompt=prompt.system,
        role=self.generation_client.enums.SYSTEM.value,
      )
    ]
    
    response = self.generation_client.generate_structured_text(
      prompt=prompt.user,
      chat_history=chat_history,
      response_model=prompt.response_model,
    )
        
    return list(prompt.response_model.model_validate_json(response)) if response else []
  

  async def rank_main_ideas(self, ideas: List[rm.MainIdea]) -> List[int]:

    if not ideas:
        return []
    
    context = "\n".join([
      idea.summary
      for idea in ideas
    ])
    
    prompt = self.prompt_template_parser.get(
        "main_idea",
        "ranking_prompt",
        {"context": context}
    )
    
    if not prompt:
      logger.error("Ranking prompt template not found")
      return []
    
    chat_history = [
      self.generation_client.construct_prompt(
        prompt=prompt.system,
        role=self.generation_client.enums.SYSTEM.value,
      )
    ]
    
    response = self.generation_client.generate_structured_text(
      prompt=prompt.user,
      chat_history=chat_history,
      response_model=prompt.response_model,
    )
    
    return list(prompt.response_model.model_validate_json(response)) if response else []