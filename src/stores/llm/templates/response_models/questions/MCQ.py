from typing import List
from pydantic import Field, model_validator
from .BaseQuestion import BaseQuestion

class MCQ(BaseQuestion):
  correct_answer: str = Field(..., min_length= 1, description="The correct answer to the question.")
  plausible_distractors: List[str] = Field(..., min_length=3, max_length=3, description="Exactly 3 distractors must be provided which the correct answer isn't one of them.")

  @model_validator(mode='after')
  def validate_model(self):
    if self.correct_answer in self.plausible_distractors:
      raise ValueError(
        f"The correct_answer '{self.correct_answer}' appears in plausible_distractors. "
        "Please replace it with a different incorrect option in the distractors list."
      )
    
    # Check plausible distractor repetition
    if len(set(self.plausible_distractors)) < len(self.plausible_distractors):
      duplicates = [item for item in set(self.plausible_distractors) if self.plausible_distractors.count(item) > 1]
      raise ValueError(f"All plausible_distractors must be unique. Duplicate values detected: {duplicates}")

    return self