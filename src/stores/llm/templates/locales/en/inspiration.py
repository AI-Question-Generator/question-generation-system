from string import Template
from stores.llm.templates.locales.PromptTemplate import PromptTemplate
from stores.llm.templates.response_models import ListOf

inspiration_prompt = PromptTemplate(
    system=Template('\n'.join([
        "Instructions:",
        "You are an expert content and curriculum designer.",
        "You will be given a text that we need to use as inspiration for educational content.",
        "Extract and creatively generate a list of distinct 'contextual situations' based on the themes, actions, or environments present in the text.",
        "",
        "Rules:",
        "- Do not summarize the text. Instead, identify and extract dynamic scenarios, environments, or activities (e.g., 'Waiting for the bus in a storm', 'A busy day at the corporate office', 'Deciding what to wear to a summer party').",
        "- These scenarios will be used later as background contexts to embed domain-specific questions.",
        "- Do not number the output.",
        "- Extract as many unique contextual situations as the text naturally supports."
    ])),
    user=Template("Source Text:\n$text"),
    response_model=ListOf[str]
)
