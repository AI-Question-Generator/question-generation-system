from string import Template
from .. import question_generation

#### QUESTION GENERATION PROMPTS. ####

# Multiple Choice Question Generation 
mcq_prompt = question_generation.mcq_prompt.model_copy()
mcq_prompt.system = Template('\n'.join([
  "Instructions:",
  "You are given a lesson on definitions, derivatives, and verbal collocations that contains target words, word families, collocations, meanings, contexts, and examples.",
  "Generate multiple choice questions that test applying these concepts in context, rather than just recalling definitions.",
  "You will be provided with *Inspiration Content*, use them combined to generate creative contextual situations for questions.",
  "",
  "Question design rules:",
  "* Each question must be a short realistic situation, sentence, or short story.",
  "* Include at least one missing part, strictly shown as: .......",
  "* Students must choose the contextually appropriate word form (derivative) or correct verbal pairing (collocation) to complete the blank.",
  "* Test word formation, precise contextual meaning, or correct verbal pairings based on the lesson.",
  "* Do NOT ask for direct dictionary definitions or literal translations.",
  "* Do NOT use phrases like 'choose the correct derivative' or 'what is the definition' in isolation.",
  "",
  "Keep sentences clear, natural, and exam style.",
  "Make distractors contextually plausible but incorrect in word form or collocation pairing.",
  "Each question must focus on only ONE definition, derivative, or verbal collocation rule.",
  "Some examples can be provided, take them as reference but never rewrite them as questions.",
  "",
  "Number of questions to generate: $num_questions",
  ]))

# True/False Question Generation 
tf_prompt = question_generation.tf_prompt.model_copy()


# Short Answer Question Generation 
short_answer_prompt = question_generation.short_answer_prompt.model_copy()