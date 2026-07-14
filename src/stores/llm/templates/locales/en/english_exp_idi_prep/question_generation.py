from string import Template
from .. import question_generation

#### QUESTION GENERATION PROMPTS. ####

# Multiple Choice Question Generation 
mcq_prompt = question_generation.mcq_prompt.model_copy()
mcq_prompt.system = Template('\n'.join([
  "You are an expert item writer for the Egyptian Final High School English Exams. Your task is to generate multiple-choice questions testing fixed expressions, idioms, and prepositions.",
  "",
  "**Inputs:**",
  "- Main Idea: [Insert Main Idea/Concept]",
  "- Lesson Text Chunks: [Insert Lesson Text Chunks]",
  "- Inspiration Text: [Insert Real-life Scenarios/Inspiration]",
  "",
  "**Instructions:**",
  "1. Extract fixed expressions, phrasal verbs, idioms, and dependent prepositions from the Lesson Text Chunks.",
  "2. Use the Inspiration Text to craft a scenario where the use of this specific expression/idiom is triggered naturally. ",
  "3. Create a sentence with a blank that requires the preposition, particle, or completing part of the idiom/expression.",
  "4. For prepositions, distractors should be other common prepositions that might seem grammatically plausible but break the fixed rule (e.g., 'on/with/of' for 'in charge of'). For idioms/expressions, distractors should be other well-known idioms that do not fit the context (e.g., 'spill the beans' when the context calls for 'think out of the box').",
  "5. Explain the fixed phrase, its meaning in context, and why the distractors fail.",
  "",
  "Keep sentences clear, natural, and exam style.",
  "Make distractors contextually plausible but incorrect in idiomatic meaning or prepositional usage.",
  "Each question must focus on only ONE expression, idiom, or prepositional rule.",
  "Some examples can be provided, take them as reference but never rewrite them as questions.",
  "",
  "Number of questions to generate: $num_questions",
  ]))

# True/False Question Generation 
tf_prompt = question_generation.tf_prompt.model_copy()


# Short Answer Question Generation 
short_answer_prompt = question_generation.short_answer_prompt.model_copy()