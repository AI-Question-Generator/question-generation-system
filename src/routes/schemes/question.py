from pydantic import BaseModel
from typing import List, Literal
from models.enums.QuestionEnum import TrueOrFalseEnum

class Question(BaseModel):
    question_statement: str
    explanation: str
    
class MCQ(Question):
    correct_answer: str
    plausible_distractors: List[str]

class TrueOrFalse(Question):
    correct_answer: Literal[TrueOrFalseEnum.TRUE.value, TrueOrFalseEnum.FALSE.value] # type: ignore

class ShortAnswer(Question):
    correct_answer: str