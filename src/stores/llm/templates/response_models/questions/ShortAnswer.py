from pydantic import Field
from . import BaseQuestion

class ShortAnswer(BaseQuestion):
  correct_answer: str = Field(..., min_length= 1, description="The correct answer to the question.")