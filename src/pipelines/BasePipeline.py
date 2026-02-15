from helpers import get_setting, Settings
from stores.llm.LLMInterface import LLMInterface


class BasePipeline:
  def __init__(self, db_client):
    self.app_settings = get_setting()
    self.db_client = db_client