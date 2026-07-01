from pydantic import Field
from typing import Literal
from models.enums.QuestionEnum import TrueOrFalseEnum
from .BaseQuestion import BaseQuestion

class TrueOrFalse(BaseQuestion):
  correct_answer: Literal[TrueOrFalseEnum.TRUE.value, TrueOrFalseEnum.FALSE.value] = Field(..., min_length=1, description="The correct answer to the question.")  # type: ignore