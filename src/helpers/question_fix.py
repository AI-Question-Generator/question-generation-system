from pydantic import BaseModel
from stores.llm.LLMInterface import AsyncLLMInterface
from stores.llm.templates.template_parser import PromptTemplateParserInterface
from typing import Optional
import asyncio
import logging
import json

from .json_tools import pydantic_model_from_json

logger = logging.getLogger(__name__)

class AsyncQuestionFixer:
  def __init__(
    self,
    generation_client: AsyncLLMInterface,
    prompt_template_parser: PromptTemplateParserInterface,      
  ):
    self.generation_client = generation_client
    self.prompt_template_parser = prompt_template_parser

  async def fix_question(self, question_dict: dict, exception_message: str, response_model: type[BaseModel]) -> Optional[BaseModel]:
    prompt_template = self.prompt_template_parser.get(
      "question_fix",
      "question_fix_prompt",
      vars={
        "json_schema": json.dumps(response_model.model_json_schema(), ensure_ascii=False),
        "json_object": question_dict,
        "error": exception_message
      }
    )

    if not prompt_template:
      logger.error("Prompt template for question fixing not found")
      return None
    
    system_message, user_message, _ = prompt_template

    if not system_message or not user_message:
      logger.error("Invalid prompt template format for question fixing")
      return None
    
    chat_history = [
      self.generation_client.construct_prompt(
        prompt=system_message,
        role=self.generation_client.enums.SYSTEM.value,
      )
    ]

    response = await self.generation_client.generate_structured_text(
      prompt=user_message,
      chat_history=chat_history,
      response_model=response_model,
    )

    try:
      return pydantic_model_from_json(response, response_model)
    except Exception as exc:
      logger.error(f"Failed to fix questions, exception:\n{exc}.\n\nResponse:\n{response}")
      return None

  async def fix_batch_questions(
    self,
    questions: list[dict],
    exception_messages: list[str],
    response_model: type[BaseModel],
  ) -> list[Optional[BaseModel]]:
    return await asyncio.gather(
      *(self.fix_question(question, exception_message, response_model) for question, exception_message in zip(questions, exception_messages))
    )
    
  

    