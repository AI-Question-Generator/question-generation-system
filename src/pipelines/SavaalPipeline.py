from helpers import get_setting, Settings
from stores.llm.LLMInterface import  AsyncLLMInterface # LLMInterface
from .BasePipeline import BasePipeline
from controllers import ProcessController, MainIdeaController
from typing import List, Dict
from bson.objectid import ObjectId
from datetime import datetime, timezone
from models import MainIdeaModel
from models.db_schemas import MainIdea
from models.ChunkModel import ChunkModel
from typing import Optional
# from stores.llm.templates.locales import en, ar
from stores.llm.templates.locales.en import question_generation
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
  async def run_question_generation(self,
                                    main_idea_ids: Optional[List[str]] = None,
                                    question_types: Optional[List[str]] = None,
                                    questions_per_idea: int = 2) -> Dict:
      """Generate questions from main ideas."""
      main_idea_model = await MainIdeaModel.create_instance(self.db_client)
          
      if main_idea_ids:
          ideas = [
              await main_idea_model.get_main_idea_record(idea_id)
              for idea_id in main_idea_ids
          ]
      else:
          ideas = await main_idea_model.get_project_main_ideas(project_id=self.project_id)
      
      if not ideas:
          return {
              "status": "failed",
              "ideas_processed": 0,
              "questions_generated": 0,
              "questions_by_type": {},
          }
      
      all_questions = {}
      total_questions = 0
      
      for idea in ideas:
          chunk_ids = idea.main_idea_chunk_ids or []
          if not chunk_ids:
              continue
          
          chunk_model = await ChunkModel.create_instance(self.db_client)
          chunks = await chunk_model.get_many_chunks_by_id(chunk_ids[:5])
          
          if not chunks:
              continue
          
          passages = "\n".join([chunk.chunk_text for chunk in chunks])
          
          idea_questions = {}
          
          q_types = question_types
          
          if q_types is None:
            q_types = ["mcq", "tf", "short_answer"]
          
          for q_type in q_types:
              questions = await self._generate_questions(
                  idea=idea,
                  passages=passages,
                  num_questions=questions_per_idea,
                  question_type=q_type
              )
              idea_questions[q_type] = questions
              total_questions += len(questions)
          
          all_questions[str(idea.id)] = idea_questions
      
      questions_by_type = {"mcq": 0, "tf": 0, "short_answer": 0}
      for idea_questions in all_questions.values():
          for q_type, questions in idea_questions.items():
              if q_type in questions_by_type:
                  questions_by_type[q_type] += len(questions)
      
      return {
          "status": "success",
          "ideas_processed": len(all_questions),
          "questions_generated": total_questions,
          "questions_by_type": questions_by_type,
          "message": f"Generated {total_questions} questions from {len(all_questions)} ideas"
      }
          


  async def _generate_questions(self,
                                idea,
                                passages: str,
                                num_questions: int,
                                question_type: str) -> List:

      """Generate questions of a specific type."""

      prompt_map = {
          "mcq": question_generation.mcq_prompt,
          "tf": question_generation.tf_prompt,
          "short_answer": question_generation.short_answer_prompt,
      }
      
      prompt_template = prompt_map.get(question_type)
      if not prompt_template:
          return []
      
      try:
          system = prompt_template.system.substitute(num_questions=num_questions)
          user = prompt_template.user.substitute(
              main_idea=idea.main_idea_summary,
              passages=passages
          )
          
          chat_history = [
              self.llm_client.construct_prompt(
                  prompt=system,
                  role=self.llm_client.enums.SYSTEM.value,
              )
          ]
          
          response = await self.llm_client.generate_structured_text(
              prompt=user,
              chat_history=chat_history,
              response_model=prompt_template.response_model,
          )
          
          return list(prompt_template.response_model.model_validate_json(response)) if response else []
          
      except Exception as e:
          logger.error(f"Error generating {question_type} questions: {str(e)}")
          return []