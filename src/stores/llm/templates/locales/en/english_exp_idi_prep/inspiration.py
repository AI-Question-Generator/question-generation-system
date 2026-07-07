from string import Template
from .. import inspiration

# Clone the base prompt so we don't accidentally mutate it
inspiration_prompt = inspiration.inspiration_prompt
