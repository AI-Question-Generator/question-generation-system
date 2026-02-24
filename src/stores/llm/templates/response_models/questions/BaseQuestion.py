from pydantic import BaseModel

class BaseQuestion(BaseModel):
  question_statement: str
  explanation: str