from enum import Enum

class QuestionEnum(Enum):
    TRUE_FALSE = 'tf'
    MULTIPLE_CHOICE = 'mcq'
    SHORT_ANSWER = 'short_answer'

class TrueOrFalseEnum(Enum):
    TRUE = "True"
    FALSE = "False"