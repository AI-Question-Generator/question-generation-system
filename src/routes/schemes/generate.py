from pydantic import BaseModel
from typing import List
from stores.llm.templates.response_models.questions import BaseQuestion, MCQ, TrueOrFalse, ShortAnswer
from models.enums.QuestionEnum import QuestionTypeEnum


class QuestionTypeRequest(BaseModel):
  type: QuestionTypeEnum
  count: int

class ProjectQuestionRequest(BaseModel):
  project_id: str
  questions: List[QuestionTypeRequest]

class QuestionsRequest(BaseModel):
  question_requests: List[ProjectQuestionRequest]

class ProjectQuestionResponse(BaseModel):
  project_id: str
  questions: List[type[BaseQuestion]]

class GenerationRequest(BaseModel):
  content: List[ProjectQuestionRequest]
  
class GenerationResponse(BaseModel):
  content: List[ProjectQuestionResponse]