import json_repair
from typing import Optional
from pydantic import BaseModel

def json_repair_loads(json_string, schema=None, salvage=True) -> Optional[dict]:
    try:
        repaired_json = json_repair.loads(json_string, schema=schema, schema_repair_mode='salvage' if salvage else 'standard')
        return repaired_json
    except Exception as e:
        print(f"Error repairing JSON: {e}")
        return None

def pydantic_model_from_json(json_string, model_class, salvage=True) -> Optional[type[BaseModel]]:
    try:
        repaired_json = json_repair_loads(json_string, schema=model_class, salvage=salvage)
        if repaired_json is not None:
            return model_class.model_validate(repaired_json)
        else:
            print("Failed to repair JSON, cannot create Pydantic model.")
            return None
    except Exception as e:
        print(f"Error creating Pydantic model: {e}")
        return None