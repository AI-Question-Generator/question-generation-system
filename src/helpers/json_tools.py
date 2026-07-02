import json_repair
from typing import Optional
from pydantic import BaseModel

def json_repair_loads(json_string, schema=None, salvage=True) -> Optional[dict]:
  repaired_json = json_repair.loads(json_string, schema=schema, schema_repair_mode='salvage' if salvage else 'standard')
  return repaired_json

def pydantic_model_from_json(json_string, model_class, salvage=True) -> Optional[BaseModel]:
  repaired_json = json_repair_loads(json_string, schema=model_class, salvage=salvage)
  return model_class.model_validate(repaired_json)