from pydantic import BaseModel
from typing import List, Literal
from models.enums.QuestionEnum import TrueOrFalseEnum

class BaseQuestion(BaseModel):
    question_statement: str
    explanation: str
    
class MCQ(BaseQuestion):
    correct_answer: str
    plausible_distractors: List[str]

class TrueOrFalse(BaseQuestion):
    correct_answer: Literal[TrueOrFalseEnum.TRUE.value, TrueOrFalseEnum.FALSE.value] # type: ignore

class ShortAnswer(BaseQuestion):
    correct_answer: str