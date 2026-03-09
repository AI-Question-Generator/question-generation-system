from pydantic import BaseModel, Field

class BaseQuestion(BaseModel):
  question_statement: str = Field(..., min_length=1, description="The text of the question being asked.")
  explanation: str = Field(..., min_length=1, description="An explanation of why provided correct answer is correct.")