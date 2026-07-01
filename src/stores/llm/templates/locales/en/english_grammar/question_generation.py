from string import Template
from stores.llm.templates.locales.PromptTemplate import PromptTemplate
# from routes.schemes.question import MCQ, ShortAnswer, TrueOrFalse
from typing import List
from .. import question_generation

#### QUESTION GENERATION PROMPTS. ####

# Multiple Choice Question Generation 
mcq_prompt = question_generation.mcq_prompt.model_copy()
mcq_prompt.system = Template('\n'.join([
  "Instructions:",
  "You are given a grammar lesson that contains rules, structures, and examples.",
  "Generate multiple-choice grammar questions that test applying these rules in context, not defining them.",
  "You will be provided with *Inspiration Content*, use them combined to generate creative contextual situations for questions.",
  "",
  "Question design rules:",
  "- Each question must be a short real-life situation, sentence, or mini-story.",
  "- Include at least one missing part, strictly shown as: .......",
  "- Students must choose the grammatically correct word or phrase to complete the blank.",
  "- Test tense, structure, prepositions, connectors, or form based on the lesson.",
  "- Do NOT ask about rules or explanations directly.",
  "- Do NOT use phrases like 'which rule', 'grammar rule', or 'tense usage'.",
  "",
  "Keep sentences clear, natural, and exam-style.",
  "Make distractors grammatically plausible but incorrect.",
  "Each question must focus on only ONE grammar concept.",
  "Some examples can be provided, take them as reference but never rewrite them as questions",
  "",
  "Number of questions to generate: $num_questions",
]))


# True/False Question Generation 
tf_prompt = question_generation.tf_prompt.model_copy()


# Short Answer Question Generation 
short_answer_prompt = question_generation.short_answer_prompt.model_copy()