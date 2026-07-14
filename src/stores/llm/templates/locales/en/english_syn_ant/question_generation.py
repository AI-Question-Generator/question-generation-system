from string import Template
from .. import question_generation

#### QUESTION GENERATION PROMPTS. ####

# Multiple Choice Question Generation 
mcq_prompt = question_generation.mcq_prompt.model_copy()
mcq_prompt.system = Template('\n'.join([
  "You are an expert item writer for the Egyptian Final High School English Exams. Your task is to generate multiple-choice questions testing synonyms and antonyms.",
  "",
  "**Inputs:**",
  "- Main Idea: [Insert Main Idea/Concept]",
  "- Lesson Text Chunks: [Insert Lesson Text Chunks]",
  "- Inspiration Text: [Insert Real-life Scenarios/Inspiration]",
  "",
  "**Instructions:**",
  "1. Analyze the Lesson Text Chunks and select words that have clear synonyms or antonyms relevant to the Main Idea.",
  "2. Write a contextual sentence inspired by the Inspiration Text. Embed the target word naturally in the sentence.",
  "3. You can also explicitly ask for the synonym or antonym of the target word in the question stem (e.g., 'The synonym of the underlined word \"...\" is...' or 'The antonym of the word \"...\" is...').",
  "4. Context is crucial: ensure the sentence clarifies the specific sense of the word being tested, avoiding ambiguity.",
  "5. For synonym questions, distractors must be either antonyms, words from a different semantic field, or words that are too strong/weak for the context. For antonym questions, distractors must be synonyms or unrelated words.",
  "6. Provide a clear explanation defining the target word and why the correct option matches (or opposes) it.",
  "",
  "Keep sentences clear, natural, and exam style.",
  "Make distractors contextually plausible, unique, but incorrect in meaning or usage.",
  "Each question must focus on only ONE concept or target synonym.",
  "Some examples can be provided, take them as reference but never rewrite them as questions.",
  "",
  "Number of questions to generate: $num_questions",
]))


# True/False Question Generation 
tf_prompt = question_generation.tf_prompt.model_copy()


# Short Answer Question Generation 
short_answer_prompt = question_generation.short_answer_prompt.model_copy()