from typing import List
from . import BaseQuestion

class MCQ(BaseQuestion):
  correct_answer: str
  plausible_distractors: List[str]