from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
  file_id : Optional[str] = None
  chunk_size: Optional[int] = 200
  overlap_size: Optional[int] = 30
  do_reset: Optional[int] = 0
  