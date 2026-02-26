from helpers import get_setting, Settings
from stores.llm.LLMInterface import  AsyncLLMInterface # LLMInterface
from .BasePipeline import BasePipeline
from controllers import ProcessController, MainIdeaController
from typing import List, Dict
from bson.objectid import ObjectId
from datetime import datetime, timezone
from models import MainIdeaModel
from models.db_schemas import MainIdea
import logging

logger = logging.getLogger(__name__)


class SavaalPipeline(BasePipeline):
  
  def __init__(self, db_client, vectordb_client, llm_client, embedding_client, template_parser, project_id: str):
    
    super().__init__(db_client=db_client)
    self.vectordb_client = vectordb_client
    self.llm_client = llm_client
    self.embedding_client = embedding_client
    self.template_parser = template_parser
    self.project_id = project_id
  
    self.main_idea_controller = MainIdeaController( generation_client=self.llm_client, 
                                                    embedding_client=self.embedding_client, 
                                                    prompt_template_parser=self.template_parser)
  async def extract_candidates_from_sections(self, sections: List[str]):
    """Extract candidate ideas from sections in parallel."""
    extracted_candidates = await self.main_idea_controller.extract_candidates_from_sections(sections=sections)
    return extracted_candidates

  async def combine_candidates(self,  candidates):
    """Combine and consolidate candidate ideas."""
    combined_candidates = await self.main_idea_controller.combine_candidates(candidates=candidates)
    return combined_candidates
  
  async def reduce_candidates(self, candidates):
    """Reduce candidates when there are too many."""
    if len(candidates) > 10:
      reduced_candidates = await self.main_idea_controller.reduce_candidates(candidates=candidates)
      return reduced_candidates
    
    return candidates
    
  
  async def rank_main_ideas(self, ideas):
    """Rank ideas by importance."""
    ranked_ideas = await self.main_idea_controller.rank_main_ideas(ideas=ideas)
    return ranked_ideas
  
  async def associate_chunks_to_ideas(self, main_ideas, ranked_ideas, top_k_chunks: int = 5) -> Dict:
    """Associate chunks to ideas via vector search."""
    idea_chunk_mapping = {}
    
    for idea, rank in zip(main_ideas, ranked_ideas):
      idea_embedding = await self.embedding_client.embed_text(idea.summary)
      search_results = self.vectordb_client.search_by_vector(
        collection_name=f"collection_{self.project_id}",
        vector=idea_embedding,
        limit=top_k_chunks
      )
      
      chunk_ids = [ObjectId(str(res.id)) for res in search_results] if search_results else []
      idea_chunk_mapping[idea.summary] = chunk_ids
    
    return idea_chunk_mapping
  
  async def save_main_ideas(self, main_ideas, ranked_ideas, idea_chunk_mapping: Dict, main_idea_model: MainIdeaModel) -> int:
    """Save main ideas with chunk associations to database."""
    main_idea_records = []
    
    for idea, rank in zip(main_ideas, ranked_ideas):
      chunk_ids = idea_chunk_mapping.get(idea.summary, [])
      
      main_idea_obj = MainIdea(
        main_idea_project_id=ObjectId(self.project_id) if isinstance(self.project_id, str) else self.project_id,
        main_idea_name=idea.name[:100],
        main_idea_summary=idea.summary,
        main_idea_rank=rank,
        main_idea_chunk_ids=chunk_ids,
        pushed_at=datetime.now(timezone.utc)
      )
      main_idea_records.append(main_idea_obj)
    
    if main_idea_records:
      saved_count = await main_idea_model.insert_many_main_ideas(main_ideas=main_idea_records)
      logger.info(f"Successfully saved {saved_count} main ideas")
      return saved_count
    
    logger.warning("No main idea records to save")
    return 0
  
  async def run_main_idea_extraction(self, sections: List[str]) -> Dict:
    """
    Complete extraction pipeline: extract → combine → reduce → rank
    """

    extracted_candidates = await self.extract_candidates_from_sections(sections)
    combined_candidates = await self.combine_candidates(extracted_candidates)
    reduced_candidates = await self.reduce_candidates(combined_candidates)
    ranked_ideas = await self.rank_main_ideas(reduced_candidates)

    return {
      "main_ideas": reduced_candidates,
      "ranked_ideas": ranked_ideas,
      "extracted_candidates_count": len(extracted_candidates),
      "combined_candidates_count": len(combined_candidates),
      "final_count": len(reduced_candidates)
    }
  ## generation part
  