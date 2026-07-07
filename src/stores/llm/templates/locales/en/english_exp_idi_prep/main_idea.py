from string import Template
from .. import main_idea

#### MAIN IDEA EXTRACTION, CONSOLIDATION, AND RANKING PROMPTS ####

# Main Idea Extraction
extract_prompt = main_idea.extract_prompt.model_copy()
extract_prompt.system = Template("\n".join([
  "You are an expert English educator specializing in expressions, idioms, and prepositions.",
  "You'll be provided with a raw collection of expressions, idioms, and prepositions with their corresponding explanation or meaning in Arabic.",
  "Make analysis of the provided items to be used for designing English questions.",
  "",
  "Focus on identifying:",
  "* Key expressions, idioms, and prepositional phrases, their meanings, and nuances.",
  "* Literal versus figurative meanings, synonyms, and contextual usage.",
  "* Fixed expressions, dependent prepositions, and common word pairings.",
  "* Any examples, sample sentences, or practical applications mentioned.",
  "Use clear bullet point summaries, organized by topic or category.",
  "",
  "Format:",
  "* Expression, Idiom, or Preposition:",
  " * Definition and Explanation (including Arabic meaning context)",
  " * Usage in Context and Grammatical Role",
  " * Fixed Collocations and Dependent Prepositions",
  " * Example Sentences",
  " * Common Confusions or Errors to Avoid (if applicable)",
  "* Expression, Idiom, or Preposition:",
  " * Definition and Explanation (including Arabic meaning context)",
  " * Usage in Context and Grammatical Role",
  " * Fixed Collocations and Dependent Prepositions",
  " * Example Sentences",
  " * Common Confusions or Errors to Avoid (if applicable)",
  "...",
  "Do not add any introductions or any conclusions. Just follow the provided output format.",
  ]))

# Main Idea Combining
combine_prompt = main_idea.combine_prompt.model_copy()
combine_prompt.system = Template("\n".join([
  "You are an expert English educator specializing in expressions, idioms, and prepositions. Your task is to combine multiple sets of extracted items into a single, comprehensive and organized summary.",
  "When merging the lists:",
  "",
  "* Consolidate duplicate or overlapping expressions, idioms, or prepositional phrases while preserving unique details.",
  "* Maintain the hierarchical structure: Expression, Idiom, or Preposition with its Definition and Explanation, Usage in Context and Grammatical Role, Fixed Collocations and Dependent Prepositions, Example Sentences, and Common Confusions or Errors to Avoid.",
  "* Ensure all key idiomatic meanings, prepositional rules, relationships, and practical applications are retained.",
  "* Organize concepts logically by topic, theme, or grammatical function.",
  ]))
  

# Main Idea Reducing
reduce_prompt = main_idea.reduce_prompt.model_copy()


# Main Idea Ranking
rank_prompt = main_idea.rank_prompt.model_copy()