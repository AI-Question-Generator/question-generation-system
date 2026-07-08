from string import Template
from .. import question_generation

#### QUESTION GENERATION PROMPTS. ####

# Multiple Choice Question Generation 
mcq_prompt = question_generation.mcq_prompt.model_copy()
mcq_prompt.system = Template('\n'.join([
  "Instructions:",
  "You are given a vocabulary lesson that contains target words, meanings, contexts, and examples.",
  "Generate multiple choice vocabulary questions that test applying these words in context, rather than just recalling definitions.",
  "You will be provided with *Inspiration Content*, use them combined to generate creative contextual situations for questions.",
  "",
  "Question design rules:",
  "- Each question must be a short realistic situation, sentence, or short story.",
  "- Include at least one missing part, strictly shown as: .......",
  "- Students must choose the contextually appropriate vocabulary word or phrase to complete the blank.",
  "- Test word meaning, synonyms, antonyms, collocations, or phrasal verbs based on the lesson.",
  "- Do NOT ask for direct dictionary definitions.",
  "- Do NOT use phrases like 'what is the definition of', 'which word means', or 'choose the synonym'.",
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