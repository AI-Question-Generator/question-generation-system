from helpers import get_setting, Settings
from stores.llm.LLMInterface import LLMInterface
from .BasePipeline import BasePipeline
from controllers import ProcessController, MainIdeaController


class SavaalPipeline(BasePipeline):
  
  def __init__(self, db_client, vectordb_client, llm_client, embedding_client, template_parser, project_id: str):
    
    super().__init__(db_client=db_client)
    self.vectordb_client = vectordb_client
    self.llm_client = llm_client
    self.embedding_client = embedding_client
    self.template_parser = template_parser
    self.project_id = project_id
  
    self.main_idea_controller = MainIdeaController( db_client=self.db_client,
                                                    llm_client=self.llm_client, 
                                                    embedding_client=self.embedding_client, 
                                                    vectordb_client=self.vectordb_client,
                                                    template_parser=self.template_parser,
                                                    project_id=self.project_id)

  async def extract(self, sections, language, domain):
    
    extracted_candidates = await self.main_idea_controller.extract_candidates_from_sections(
            sections=sections,
            language=language,
            domain=domain
          )
  
    return extracted_candidates

  
  async def reduce(self, candidates, language, domain):
    
    combined_candidates = await self.main_idea_controller.combine_candidates(
                candidates=candidates,
                language=language,
                domain=domain
              )
    
    if len(combined_candidates) > 10:
      reduced_candidates = await self.main_idea_controller.reduce_candidates(
        candidates=combined_candidates,
        language=language,
        domain=domain
      )
      return reduced_candidates
  
    return combined_candidates
  
  async def rank(self, ideas, language, domain):
    ranked_ideas = await self.main_idea_controller.rank_main_ideas(
        ideas=ideas,
        language=language,
        domain=domain
      )
    
    return ranked_ideas
  
  async def retrieve(self, ranked_ideas):
    
    idea_chunk_mapping = self.main_idea_controller.associate_chunks_to_ideas(
        main_ideas=ranked_ideas,
        # top_k=5
      )
    return idea_chunk_mapping

  async def run_main_idea_extraction(self, sections, language, domain):

    extracted_candidates = await self.extract(sections, language, domain)
    reduced_candidates = await self.reduce(extracted_candidates, language, domain)
    ranked_ideas = await self.rank(reduced_candidates, language, domain)
    idea_chunk_mapping = await self.retrieve(ranked_ideas)

    saved_count = await self.main_idea_controller.save_main_ideas_batch(
        ideas=reduced_candidates,
        ranked_ideas=ranked_ideas,
        idea_chunk_mapping=idea_chunk_mapping
      )

    return {
        "extracted_count": len(extracted_candidates),
        "reduced_count": len(reduced_candidates),
        "ranked_count": len(ranked_ideas),
        "saved_count": saved_count,
      }
  
  ## generation part
  