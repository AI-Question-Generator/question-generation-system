from string import Template
from .. import main_idea

#### MAIN IDEA EXTRACTION, CONSOLIDATION, AND RANKING PROMPTS ####

# Main Idea Extraction
extract_prompt = main_idea.extract_prompt.model_copy()
extract_prompt.system = Template("\n".join([
  "You are an expert English educator specializing in definitions, derivatives, and verbal collocations.",
  "You'll be provided with a raw collection of words with their corresponding explanation or meaning in Arabic.",
  "Make analysis of the provided items to design English questions.",
  "",
  "Focus on identifying:",
  "* Key root words, their core definitions, and nuances.",
  "* Word families and derivatives, including changes in part of speech via prefixes or suffixes.",
  "* Verbal collocations, such as fixed verb and noun, verb and adverb, or verb and preposition pairings.",
  "* Any examples, sample sentences, or practical applications mentioned.",
  "Use clear bullet point summaries, organized by topic or category.",
  "",
  "Format:",
  "* Root Word, Derivative, or Verbal Collocation:",
  " * Definition and Explanation (including Arabic meaning context)",
  " * Word Family and Derivatives OR Collocating Partners",
  " * Usage in Context and Grammatical Role",
  " * Example Sentences",
  " * Common Confusions or Errors to Avoid (if applicable)",
  "* Root Word, Derivative, or Verbal Collocation:",
  " * Definition and Explanation (including Arabic meaning context)",
  " * Word Family and Derivatives OR Collocating Partners",
  " * Usage in Context and Grammatical Role",
  " * Example Sentences",
  " * Common Confusions or Errors to Avoid (if applicable)",
  "...",
  "Do not add any introductions or any conclusions. Just follow the provided output format.",
  ]))

# Main Idea Combining
combine_prompt = main_idea.combine_prompt.model_copy()
combine_prompt.system = Template("\n".join([
  "You are an expert English educator specializing in definitions, derivatives, and verbal collocations. Your task is to combine multiple sets of extracted items into a single, comprehensive and organized summary.",
  "When merging the lists:",
  "",
  "* Consolidate duplicate or overlapping root words, derivatives, or collocations while preserving unique details.",
  "* Maintain the hierarchical structure: Root Word, Derivative, or Verbal Collocation with its Definition, Word Family or Collocating Partners, Usage in Context, Example Sentences, and Common Confusions or Errors to Avoid.",
  "* Ensure all key meanings, morphological relationships, collocation rules, and practical applications are retained.",
  "* Organize concepts logically by root word, morphological category, or thematic topic.",
  ]))
  

# Main Idea Reducing
reduce_prompt = main_idea.reduce_prompt.model_copy()


# Main Idea Ranking
rank_prompt = main_idea.rank_prompt.model_copy()