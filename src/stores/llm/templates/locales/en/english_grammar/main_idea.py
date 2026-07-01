from string import Template
from stores.llm.templates.locales.PromptTemplate import PromptTemplate
from typing import List
from .. import main_idea

#### MAIN IDEA EXTRACTION, CONSOLIDATION, AND RANKING PROMPTS ####

# Main Idea Extraction
extract_prompt = main_idea.extract_prompt.model_copy()
extract_prompt.system = Template("\n".join([
  "You are an expert English grammar educator specializing in analyzing grammar lessons and texts. Given the following excerpt from a grammar lesson or text, extract the main grammar concepts, rules, and supporting details that are critical to understanding the material.",
  "Focus on identifying:",
  "",
  "- Key grammar concepts, rules, or structures introduced in the text.",
  "- Definitions or explanations of these grammar concepts.",
  "- Usage patterns and relationships between grammar elements.",
  "- Any examples, sample sentences, or practical applications mentioned.",
  "",
  "Use clear, bullet-point summaries, organized by grammar topic.",
  "Format:",
  "- Grammar Concept/Rule:",
  " - Definition/Explanation",
  " - Usage Rules/Patterns",
  " - Example Sentences",
  " - Common Errors to Avoid (if applicable)",
  "- Grammar Concept/Rule:",
  " - Definition/Explanation",
  " - Usage Rules/Patterns",
  " - Example Sentences",
  " - Common Errors to Avoid (if applicable)",
  "...",
  "Do not add any introductions or any conclusions. Just follow the provided output format.",
  ]))

# Main Idea Combining
combine_prompt = main_idea.combine_prompt.model_copy()
combine_prompt.system = Template("\n".join([
  "You are an expert English grammar educator. Your task is to combine multiple sets of extracted grammar concepts into a single, comprehensive and organized summary.",
  "When merging the lists:",
  "",
  "- Consolidate duplicate or overlapping grammar concepts while preserving unique details.",
  "- Maintain the hierarchical structure: Grammar Concept/Rule with its Definition/Explanation, Usage Rules/Patterns, Example Sentences, and Common Errors.",
  "- Ensure all key grammar rules, relationships, and practical applications are retained.",
  "- Organize concepts logically by grammar topic or complexity level.",
  ]))
  

# Main Idea Reducing
reduce_prompt = main_idea.reduce_prompt.model_copy()


# Main Idea Ranking
rank_prompt = main_idea.rank_prompt.model_copy()