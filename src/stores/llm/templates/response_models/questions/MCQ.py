from typing import List
from pydantic import Field
from . import BaseQuestion

class MCQ(BaseQuestion):
  correct_answer: str = Field(..., min_length= 1, description="The correct answer to the question.")
  plausible_distractors: List[str] = Field(..., min_length=3, max_length=3, description="Exactly 3 distractors must be provided which the correct answer isn't one of them.")