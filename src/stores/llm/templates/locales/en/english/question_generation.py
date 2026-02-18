from string import Template
from stores.llm.templates.locales.PromptTemplate import PromptTemplate
from routes.schemes.question import MCQ, ShortAnswer, TrueOrFalse
from typing import List
from .. import question_generation

#### QUESTION GENERATION PROMPTS. ####

# Multiple Choice Question Generation 
mcq_prompt = question_generation.mcq_prompt


# True/False Question Generation 
tf_prompt = question_generation.tf_prompt


# Short Answer Question Generation 
short_answer_prompt = question_generation.short_answer_prompt