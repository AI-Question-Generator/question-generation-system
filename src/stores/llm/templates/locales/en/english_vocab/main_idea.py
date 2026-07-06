from string import Template
from stores.llm.templates.locales.PromptTemplate import PromptTemplate
from typing import List
from .. import main_idea

#### MAIN IDEA EXTRACTION, CONSOLIDATION, AND RANKING PROMPTS ####

# Main Idea Extraction
extract_prompt = main_idea.extract_prompt.model_copy()
extract_prompt.system = Template("\n".join([
  "You are an expert English vocabulary educator specializing in analyzing vocabulary lessons and texts.",
  "You'll be provided with a raw vocabulary collection with their corresponding meaning in Arabic.",
  "Make analysis of the provided vocabulary to design English vocabulary questions.",
  "Focus on identifying:",
  "",
  "- All vocabulary words, their definitions, and nuances.",
  "- Word meanings, synonyms, and antonyms.",
  "- Vocabulary in context and how words function in sentences.",
  "- Collocations, relations, phrasal usage, and common word pairings.",
  "- Any examples, sample sentences, or practical applications mentioned.",
  "",
  "Use clear bullet point summaries, organized by vocabulary topic or word category.",
  "Format:",
  "- Vocabulary Word or Concept:",
  " - Definition and Explanation",
  " - Usage in Context",
  " - Collocations and Word Pairings",
  " - Example Sentences",
  " - Common Confusions or Errors to Avoid (if applicable)",
  "...",
  "Do not add any introductions or any conclusions. Just follow the provided output format.",
  ]))

# Main Idea Combining
combine_prompt = main_idea.combine_prompt.model_copy()
combine_prompt.system = Template("\n".join([
  "You are an expert English vocabulary educator. Your task is to combine multiple sets of extracted vocabulary concepts into a single, comprehensive and organized summary.",
  "When merging the lists:",
  "",
  "- Consolidate duplicate or overlapping vocabulary words while preserving unique details.",
  "- Maintain the hierarchical structure: Vocabulary Word or Concept with its Definition and Explanation, Usage in Context, Collocations and Word Pairings, Example Sentences, and Common Confusions or Errors to Avoid.",
  "- Ensure all key vocabulary meanings, nuances, relationships, and practical applications are retained.",
  "- Organize concepts logically by vocabulary topic, theme, or complexity level.",
  "- Ensure complex relations between vocabulary (Synonyms, Antonyms, Collocations, ...etc) are stated as main ideas, not only per-word definitions."
  ]))
  

# Main Idea Reducing
reduce_prompt = main_idea.reduce_prompt.model_copy()


# Main Idea Ranking
rank_prompt = main_idea.rank_prompt.model_copy()