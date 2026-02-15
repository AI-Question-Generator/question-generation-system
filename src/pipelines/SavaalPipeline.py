from helpers import get_setting, Settings
from stores.llm.LLMInterface import LLMInterface
from .BasePipeline import BasePipeline
from controllers import ProcessController


class SavaalPipeline(BasePipeline):
  def __init__(self,
               db_client,
               vector_db_client,
               project_id: str,
               llm_provider: LLMInterface,
               embedding_provider: LLMInterface,
               ):
    super().__init__(db_client)
    self.vector_db_client = vector_db_client
    self.project_id = project_id
    self.llm_provider = llm_provider
    self.embedding_provider = embedding_provider
  
  def split_to_sections(self, )