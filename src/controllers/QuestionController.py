from stores.llm.LLMInterface import AsyncLLMInterface
from stores.llm.templates.template_parser import PromptTemplateParserInterface
from stores.llm.templates import response_models as rm
from stores.llm.templates.response_models.questions import BaseQuestion
from stores.llm.templates.response_models.list_wrapper import ListOf
from models.enums.QuestionEnum import QuestionTypeEnum
from helpers.json_tools import pydantic_model_from_json, json_repair_loads
from helpers.question_fix import AsyncQuestionFixer
from typing import List, Optional

import json
import logging

logger = logging.getLogger(__name__)

class QuestionController:
  def __init__(
    self,
    generation_client: AsyncLLMInterface,
    prompt_template_parser: PromptTemplateParserInterface,
    ):
    self.generation_client = generation_client
    self.prompt_template_parser = prompt_template_parser
  
  async def generate_questions(self, main_idea_summary: str, passages: List[str], num_questions: int, question_type: QuestionTypeEnum, inspirations: Optional[List[str]] = None) -> List[type[rm.questions.QuestionType]]:
    passages_str = "\n\n".join(passages)
    inspirations_str = "\n\n".join(inspirations) if inspirations else "(Not provided)"
    
    prompt_template = self.prompt_template_parser.get(
      "question_generation",
      f"{question_type.value.lower()}_prompt",
      vars={
        "main_idea": main_idea_summary,
        "passages": passages_str,
        "num_questions": num_questions,
        "inspirations": inspirations_str,
      }
    )
    
    if not prompt_template:
      logger.error(f"Prompt template for question type {question_type} not found")
      return []
    
    system_message, user_message, response_model = prompt_template
    list_of_response_model = ListOf.constrained(response_model, min_length=num_questions, max_length=num_questions)
    
    if not system_message or not user_message:
      logger.error(f"Invalid prompt template format for question type {question_type}")
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
      response_model=list_of_response_model,
    )

    try:
      candidates = pydantic_model_from_json(response, list_of_response_model)
      return list(candidates) if candidates else []
    except Exception as exc:
      logger.error(f'Failed to parse questions, exception:\n{exc}.\n\nResponse:\n{response}\n\nTrying to fix the questions...')
      return await self.fix_question_candidates(response, list_of_response_model)
  
  async def fix_question_candidates(self, response: str, response_model: type[rm.questions.QuestionType]) -> List[type[rm.questions.QuestionType]]:
    candidates = json_repair_loads(response, salvage=False)['root'] if response else []

    question_fixer = AsyncQuestionFixer(
      generation_client=self.generation_client,
      prompt_template_parser=self.prompt_template_parser
    )

    idx = []
    excs = []
    for i, candidate in enumerate(candidates):
      try:
        candidates[i] = pydantic_model_from_json(json.dumps(candidate, ensure_ascii=False), response_model)
      except Exception as exc:
        logger.error(f'Failed to parse question candidate at index {i}, exception:\n{exc}.\n\nCandidate:\n{candidate}')
        idx.append(i)
        excs.append(exc)

    fixed_candidates = await question_fixer.fix_batch_questions(
      questions=[candidates[i] for i in idx],
      exception_messages=[str(exc) for exc in excs],
      response_model=response_model
    )

    for i, fixed_candidate in zip(idx, fixed_candidates):
      if fixed_candidate:
        candidates[i] = fixed_candidate
      else:
        candidates[i] = json_repair_loads(json.dumps(candidates[i], ensure_ascii=False), response_model, salvage=True)
    if not fixed_candidates:
      logger.error(f'Question fixing failed for a sample, Response:\n{response}')
    
    return candidates