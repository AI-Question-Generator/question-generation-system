from string import Template
from stores.llm.templates.locales.PromptTemplate import PromptTemplate

#### QUESTION FIX PROMPT ####
question_fix_prompt = PromptTemplate(
  system=Template("\n".join([
    "Role:",
    "You are an expert JSON validator.",
    "",
    "Instructions:",
    "- You will receive a JSON Schema, an invalid JSON object, and an error description.",
    "- Fix the invalid JSON object to strictly match the JSON Schema and resolve the error."
    "- Only modify the specific attributes causing the error.",
    "- Do not alter any other attributes.",
    "- Output only valid JSON",
  ])),
  user=Template("\n".join([
    "JSON Schema:",
    "$json_schema",
    "",
    "Invalid JSON:",
    "$json_object",
    "",
    "Error Description:",
    "$error",
    "```json\n"
  ])),
)