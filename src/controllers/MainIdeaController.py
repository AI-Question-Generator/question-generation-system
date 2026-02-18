from .BaseController import BaseController
from models.db_schemas import DataChunk, MainIdea
from stores.llm.LLMEnums import DocumentTypeEnum
from helpers.config import get_setting, Settings
from typing import List, Dict, Tuple
from models.MainIdeaModel import MainIdeaModel
from models.db_schemas import MainIdea
from bson.objectid import ObjectId
from datetime import datetime, timezone
import json
import asyncio
import logging
import re

logger = logging.getLogger(__name__)

class MainIdeaController(BaseController):
  def __init__(self, db_client, llm_client, embedding_client, vectordb_client, template_parser, project_id):
    """
    Initialize MainIdeaController.
    """
    super().__init__()
    self.db_client = db_client
    self.llm_client = llm_client
    self.embedding_client = embedding_client
    self.vectordb_client = vectordb_client
    self.template_parser = template_parser
    self.project_id = project_id
        
    
  async def extract_candidates_from_sections(self, sections: List[str], language: str, domain: str) -> Dict[str, List[str]]:
  
    section_candidates = {}
    
    tasks = []
    for idx, section in enumerate(sections):
        prompt = self.template_parser.get(
            "main_idea",
            "extraction_prompt",
            {"chunks_context": section}
        )
        
        task = self.llm_client.generate_text(
            prompt=prompt,
            max_output_tokens=self.llm_client.GENERATION_DEFAULT_MAX_TOKENS,
            temperature=self.llm_client.GENERATION_DEFAULT_TEMPERATURE
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for idx, result in enumerate(results):
        ideas = result.split('\n') if result else []
        section_candidates[f"section_{idx}"] = ideas
    
    return section_candidates

  
  async def combine_candidates(self, candidates: Dict[str, List[str]], language: str, domain: str) -> List[str]:
    
    all_candidates = []
    for ideas in candidates.values():
        all_candidates.extend(ideas)
    
    if not all_candidates:
        return []
    
    extracted_candidates = "\n".join(all_candidates)
    
    prompt = self.template_parser.get(
        "main_idea",
        "combining_prompt",
        {"extracted_ideas": extracted_candidates}
    )
    
    response = self.llm_client.generate_text(
        prompt=prompt,
        max_output_tokens=self.llm_client.GENERATION_DEFAULT_MAX_TOKENS,
        temperature=self.llm_client.GENERATION_DEFAULT_TEMPERATURE
    )
    
    combined_ideas = response.split('\n') if response else []
    
    return combined_ideas
  
  async def reduce_candidates(self, candidates: List[str], language: str, domain: str) -> List[str]:
    
    if not candidates:
        return []
    
    candidates_text = "\n".join(candidates)
    
    prompt = self.template_parser.get(
        "main_idea",
        "combining_prompt",
        {"extracted_ideas": candidates_text}
    )
    
    response = self.llm_client.generate_text(
        prompt=prompt,
        max_output_tokens=self.llm_client.GENERATION_DEFAULT_MAX_TOKENS,
        temperature=self.llm_client.GENERATION_DEFAULT_TEMPERATURE
    )
    
    reduced_ideas = response.split('\n') if response else []
    
    return reduced_ideas
  

  async def rank_main_ideas(self, ideas: List[str], language: str, domain: str) -> List[Tuple[str, int]]:

    if not ideas:
        return []
    
    ideas_text = "\n".join([f"{i+1}. {idea}" for i, idea in enumerate(ideas)])
    
    prompt = self.template_parser.get(
        "main_idea",
        "ranking_prompt",
        {"main_ideas": ideas_text}
    )
    
    response = self.llm_client.generate_text(
        prompt=prompt,
        max_output_tokens=self.llm_client.GENERATION_DEFAULT_MAX_TOKENS,
        temperature=self.llm_client.GENERATION_DEFAULT_TEMPERATURE
    )
    
    ranked_ideas = []
    lines = response.split('\n') if response else []
    
    for rank, line in enumerate(lines):
        if line.strip():
            ranked_ideas.append((line.strip(), rank+1))
    
    return ranked_ideas
  
  async def associate_chunks_to_ideas(self, main_ideas: List[Tuple[str, int]], top_k: int = 5) -> Dict[str, List[str]]:

    idea_chunk_mapping = {}
    
    for idea_text, rank in main_ideas:
        # Search vector DB for relevant chunks
        results = self.vectordb_client.search_by_vector(
            collection_name=f"collection_{self.project_id}",
            vector=self.embedding_client.embed_text(idea_text),
            limit=top_k
        )
        
        # Extract chunk IDs from results
        chunk_ids = [str(result.id) for result in results] if results else []
        
        idea_chunk_mapping[idea_text] = chunk_ids
    
    return idea_chunk_mapping
  
  async def save_main_ideas_batch(self, ideas: List[str], ranked_ideas: List[Tuple[str, int]], idea_chunk_mapping: Dict[str, List[str]]) -> int:

    main_idea_model = await MainIdeaModel.create_instance(db_client=self.db_client)
    
    main_idea_records = []
    
    for idea_text, rank in ranked_ideas:
        chunk_ids = idea_chunk_mapping.get(idea_text, [])
        
        chunk_object_ids = [ObjectId(cid) for cid in chunk_ids if cid]
        
        main_idea = MainIdea(
            main_idea_project_id=ObjectId(self.project_id) if isinstance(self.project_id, str) else self.project_id,
            main_idea_name=idea_text[:100],
            main_idea_summary=idea_text,
            main_idea_rank=rank,
            # main_idea_metadata={"language": "en", "domain": "general"},
            main_idea_chunk_ids=chunk_object_ids,
            pushed_at=datetime.now(timezone.utc)
        )
        
        main_idea_records.append(main_idea)
    
    inserted = await main_idea_model.insert_many_main_ideas(main_ideas=main_idea_records)
    
    return inserted