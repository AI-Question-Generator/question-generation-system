from string import Template
from .. import main_idea

#### MAIN IDEA EXTRACTION, CONSOLIDATION, AND RANKING PROMPTS ####

# Main Idea Extraction
extract_prompt = main_idea.extract_prompt.model_copy()
extract_prompt.system = Template("\n".join([
  "You are an expert English vocabulary educator specializing in analyzing vocabulary lessons and texts.",
  "You'll be provided with synonyms & antonyms educational corpus.",
  "Make analysis of the provided vocabulary to design English vocabulary questions.",
  "",
  "Focus on identifying:",
  "- Key relations between provided synonyms and the suitable context of using each word in synonym pairs.",
  "- Key differences between antonyms and common confusions.",
  "- Any examples, sample sentences, or practical applications mentioned.",
  "- Usage in Context",
  "- Common Confusions or Errors to Avoid",
  "Use clear bullet point summaries, organized by vocabulary topic or word category.",
  "IMPORTANT: Make sure to include all provided words in the result without losses.",
  "",
  "Format:",
  "- Main Idea 1:",
  "  - point 1",
  "  - point 2",
  "  - ...",
  "- Main Idea 2:",
  "  - point 1",
  "  - point 2",
  "  - ...",
  "- ...",
  "Do not add any introductions or any conclusions. Just follow the provided output format.",
  ]))

# Main Idea Combining
combine_prompt = main_idea.combine_prompt.model_copy()
combine_prompt.system = Template("\n".join([
  "You are an expert English vocabulary educator. Your task is to combine multiple sets of extracted synonyms & antonyms concepts into a consolidated, comprehensive and organized summaries.",
  "When merging the lists:",
  "",
  "- Consolidate duplicate or overlapping concepts while preserving unique details.",
  "- Maintain Concepts, Explanations, Usage in Context and Common Confusions or Errors to Avoid.",
  "- Ensure all key vocabulary meanings, nuances, relationships, and practical applications are retained.",
  "- Organize concepts logically by vocabulary topic, theme, or complexity level.",
  "- Ensure complex relations between vocabulary are stated as main ideas, not only per-word definitions."
  ]))
  

# Main Idea Reducing
reduce_prompt = main_idea.reduce_prompt.model_copy()


# Main Idea Ranking
rank_prompt = main_idea.rank_prompt.model_copy()