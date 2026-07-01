from .BaseController import BaseController
from typing import List
from stores.llm.templates.template_parser import PromptTemplateParserInterface
from stores.llm.LLMInterface import AsyncLLMInterface
from models.InspirationModel import InspirationModel
from helpers.json_tools import pydantic_model_from_json

import asyncio
import logging

logger = logging.getLogger('uvicorn.error')


class InspirationController(BaseController):
  """Controller for generating Contextual Situations (Inspirations) from text and storing them."""

  def __init__(
    self,
    generation_client: AsyncLLMInterface,
    prompt_template_parser: PromptTemplateParserInterface,
  ):
    super().__init__()
    self.generation_client = generation_client
    self.prompt_template_parser = prompt_template_parser

  async def generate_inspirations(self, sections: List[str]) -> List[str]:
    """
    Parses text, generates inspirations for each section, and returns a deduplicated list.
    """

    tasks = []
    response_models = []
    for section in sections:
      result = self.prompt_template_parser.get(
        "inspiration", "inspiration_prompt", {"text": section}
      )
      if result is None:
        logger.error(f"Prompt Template not found")
        continue

      system_message, user_message, response_model = result
      logger.info(system_message)
      logger.info(user_message)
      logger.info(response_model)

      if not system_message or not user_message:
        logger.error("Generation prompt template not found")
        continue

      if not isinstance(user_message, str) or not isinstance(system_message, str):
        logger.error(
          "Invalid prompt template format for inspiration generation"
        )
        continue

      chat_history = [
        self.generation_client.construct_prompt(
          prompt=system_message,
          role=self.generation_client.enums.SYSTEM.value,
        )
      ]
      task = self.generation_client.generate_structured_text(
        prompt=user_message,
        chat_history=chat_history,
        response_model=response_model,
      )
      tasks.append(task)
      response_models.append(response_model)

    results = await asyncio.gather(*tasks, return_exceptions=True)
    all_inspirations = set()
    for res, model in zip(results, response_models):
      if isinstance(res, Exception):
        logger.error(f"Error generating inspiration: {res}")
        continue

      parsed_res = pydantic_model_from_json(res, model)
      if not list(parsed_res):
        logger.warning(f"Model generated Zero Inspirations")
        continue

      # Handle ListOf[str] or similar list-based response models
      items = list(parsed_res) if parsed_res else []
      for item in items:
        all_inspirations.add(item.strip())

    logger.info(
      f"Successfully generated {len(all_inspirations)} unique inspirations."
    )
    return list(all_inspirations)