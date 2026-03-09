from stores.llm.LLMInterface import LLMInterface
from stores.llm.templates.template_parser import PromptTemplateParserInterface
from stores.llm.templates import response_models as rm
from stores.llm.templates.response_models.questions import BaseQuestion
from stores.llm.templates.response_models.list_wrapper import ListOf
from models.enums.QuestionEnum import QuestionTypeEnum
from helpers.json_tools import pydantic_model_from_json
from typing import List
import logging

class QuestionController:
  def __init__(
    self,
    generation_client: LLMInterface,
    prompt_template_parser: PromptTemplateParserInterface,
    ):
    self.generation_client = generation_client
    self.prompt_template_parser = prompt_template_parser
    self.logger = logging.getLogger(__name__)
  
  async def generate_questions(self, main_idea_summary: str, passages: List[str], num_questions: int, question_type: QuestionTypeEnum) -> List[type[BaseQuestion]]:
    passages_str = "\n\n".join(passages)
    
    prompt_template = self.prompt_template_parser.get(
      "question_generation",
      f"{question_type.value.lower()}_prompt",
      vars={"main_idea": main_idea_summary, "passages": passages_str, "num_questions": num_questions}
    )
    
    if not prompt_template:
      self.logger.error(f"Prompt template for question type {question_type} not found")
      return []
    
    system_message, user_message, response_model = prompt_template
    response_model = ListOf.constrained(response_model, min_length=num_questions, max_length=num_questions)
    
    if not system_message or not user_message:
      self.logger.error(f"Invalid prompt template format for question type {question_type}")
      return []
    
    chat_history = [
      self.generation_client.construct_prompt(
        prompt=system_message,
        role=self.generation_client.enums.SYSTEM.value,
      )
    ]
    response = self.generation_client.generate_structured_text(
      prompt=user_message,
      chat_history=chat_history,
      response_model=response_model,
    )
    response = pydantic_model_from_json(response, response_model)
    return list(response) if response else []
  
  async def generate_questions_from_main_idea(self, main_idea: rm.MainIdea, passages: List[str], question_type: QuestionTypeEnum, num_questions: int) -> List[type[BaseQuestion]]:
    return await self.generate_questions(main_idea_summary=main_idea.summary, passages=passages, num_questions=num_questions, question_type=question_type)