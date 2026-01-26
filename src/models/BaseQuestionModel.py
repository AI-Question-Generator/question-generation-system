from pydantic import BaseModel
from typing import List, Literal

class BaseQuestionModel(BaseModel):
    question_statement: str
    explanation: str
    
class BaseMCQ(BaseQuestionModel):
    correct_answer: str
    plausible_distractors: List[str]

class BaseTrueOrFalse(BaseQuestionModel):
    correct_answer: Literal["True", "False"]

class BaseShortAnswer(BaseQuestionModel):
    correct_answer: str