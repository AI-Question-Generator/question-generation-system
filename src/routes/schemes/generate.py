from pydantic import BaseModel
from typing import List, Literal
from models.BaseQuestionModel import BaseQuestionModel

class QuestionTypeRequest(BaseModel):
    type: Literal["mcq", "tf", "short_answer"]
    count: int

class LessonQuestionRequest(BaseModel):
    lesson_id: str
    questions: List[QuestionTypeRequest]

class QuestionsRequest(BaseModel):
    question_requests: List[LessonQuestionRequest]

class LessonQuestionResponse(BaseModel):
    lesson_id: str
    questions: List[BaseQuestionModel]

class QuestionsResponse(BaseModel):
    content: List[LessonQuestionResponse]