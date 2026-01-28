from pydantic import BaseModel
from typing import List, Literal
from models.db_schemas.question import Question
from models.enums.QuestionEnum import QuestionTypeEnum

class QuestionTypeRequest(BaseModel):
    type: QuestionTypeEnum
    count: int

class LessonQuestionRequest(BaseModel):
    lesson_id: str
    questions: List[QuestionTypeRequest]

class QuestionsRequest(BaseModel):
    question_requests: List[LessonQuestionRequest]

class LessonQuestionResponse(BaseModel):
    lesson_id: str
    questions: List[Question]

class QuestionsResponse(BaseModel):
    content: List[LessonQuestionResponse]