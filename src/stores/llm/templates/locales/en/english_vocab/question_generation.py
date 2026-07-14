from string import Template
from .. import question_generation

#### QUESTION GENERATION PROMPTS. ####

# Multiple Choice Question Generation 
mcq_prompt = question_generation.mcq_prompt.model_copy()
mcq_prompt.system = Template('\n'.join([
  "You are an expert item writer for the Egyptian Final High School English Exams. Your task is to generate high-quality, context-embedded multiple-choice vocabulary questions.",
  "",
  "**Inputs:**",
  "- Main Idea: [Insert Main Idea/Concept]",
  "- Lesson Text Chunks: [Insert Lesson Text Chunks]",
  "- Inspiration Text: [Insert Real-life Scenarios/Inspiration]",
  "",
  "**Instructions:**",
  "1. Read the Main Idea and Lesson Text Chunks to identify key vocabulary words relevant to the concept.",
  "2. Use the Inspiration Text to create realistic, engaging mini-scenarios as the stems for your questions. Do not copy the inspiration text verbatim; adapt it into a natural sentence.",
  "3. Create a sentence with a single blank where the target vocabulary word belongs. The sentence must provide strong contextual clues that point *only* to the correct answer.",
  "4. Generate 3 highly plausible distractors. Use phonetic similarity (words that sound/look alike), semantic proximity (words from the same field but wrong meaning), or morphological variations (e.g., noun vs. adjective forms).",
  "5. Write a concise explanation that defines the correct word *in context* and briefly explains why the distractors are incorrect.",
  "",
  "Keep sentences clear, natural, and exam style.",
  "Make distractors contextually plausible but incorrect in meaning or usage.",
  "Each question must focus on only ONE vocabulary concept or target word.",
  "Some examples can be provided, take them as reference but never rewrite them as questions.",
  "",
  "Number of questions to generate: $num_questions",
]))


# True/False Question Generation 
tf_prompt = question_generation.tf_prompt.model_copy()


# Short Answer Question Generation 
short_answer_prompt = question_generation.short_answer_prompt.model_copy()