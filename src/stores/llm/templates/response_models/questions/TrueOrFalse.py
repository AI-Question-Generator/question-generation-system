from typing import Literal
from models.enums.QuestionEnum import TrueOrFalseEnum
from . import BaseQuestion

class TrueOrFalse(BaseQuestion):
  correct_answer: Literal[TrueOrFalseEnum.TRUE.value, TrueOrFalseEnum.FALSE.value] # type: ignore