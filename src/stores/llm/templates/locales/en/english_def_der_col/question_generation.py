from string import Template
from .. import question_generation

#### QUESTION GENERATION PROMPTS. ####

# Multiple Choice Question Generation 
mcq_prompt = question_generation.mcq_prompt.model_copy()
mcq_prompt.system = Template('\n'.join([
  "You are an expert item writer for the Egyptian Final High School English Exams. Your task is to generate multiple-choice questions testing definitions, word derivatives, and verbal/noun collocations.",
  "",
  "**Inputs:**",
  "- Main Idea: [Insert Main Idea/Concept]",
  "- Lesson Text Chunks: [Insert Lesson Text Chunks]",
  "- Inspiration Text: [Insert Real-life Scenarios/Inspiration]",
  "",
  "**Instructions:**",
  "1. **Definitions:** Frame the target word's definition as the sentence stem, having a blank (e.g., \"Harm or injury that results from... is called .........\").",
  "2. **Derivatives:** Use the Inspiration Text to write a sentence where a root word must be transformed into a specific part of speech (noun, verb, adjective, adverb) to be grammatically correct. Distractors must be other derivative forms of the same root (e.g., apprentice vs. apprenticeship, trainee vs. trainer).",
  "3. **Collocations:** Identify strict verb-noun or adjective-noun partnerships from the text (e.g., 'reach a conclusion', 'career direction'). Create sentences where the collocating verb or adjective is missing. Distractors must be verbs/nouns that are semantically plausible but do not naturally collocate.",
  "4. Provide an explanation that addresses the grammatical rule, the definition, or the specific collocational bond.",
  "",
  "Number of questions to generate: $num_questions",
  ]))

# True/False Question Generation 
tf_prompt = question_generation.tf_prompt.model_copy()


# Short Answer Question Generation 
short_answer_prompt = question_generation.short_answer_prompt.model_copy()