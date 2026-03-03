from string import Template
from stores.llm.templates.locales.PromptTemplate import PromptTemplate
from typing import List
from .. import main_idea

#### MAIN IDEA EXTRACTION, CONSOLIDATION, AND RANKING PROMPTS ####

# Main Idea Extraction
extract_prompt = main_idea.extract_prompt


# Main Idea Combining
combine_prompt = main_idea.combine_prompt


# Main Idea Reducing
reduce_prompt = main_idea.reduce_prompt


# Main Idea Ranking
rank_prompt = main_idea.rank_prompt