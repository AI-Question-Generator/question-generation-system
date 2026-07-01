from string import Template
from .. import inspiration

# Clone the base prompt so we don't accidentally mutate it
inspiration_prompt = inspiration.inspiration_prompt.model_copy()

# Override only the system prompt to tailor it specifically for English Grammar
inspiration_prompt.system = Template('\n'.join([
    "Instructions:",
    "You are an expert educational curriculum designer.",
    "You will be given inspiration content, use it to generate creative contextual situations.",
    "Extract and creatively generate a list of distinct 'contextual situations' based on the themes, actions, or environments present in the inspiration content.",
    "",
    "Rules:",
    "- Do not summarize the text. Instead, identify and extract dynamic scenarios or activities (e.g., 'Waiting for the bus in a storm', 'A busy day at the corporate office', 'Deciding what to wear to a summer party').",
    "- These scenarios will be used later as background contexts to naturally embed English grammar questions.",
    "- Do not number the output.",
    "- Extract as many unique contextual situations as the text naturally supports."
]))
