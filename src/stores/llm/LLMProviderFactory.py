from .LLMEnums import LLMEnums

class LLMProviderFactory:
  def __init__(self, config: dict):
    self.config = config
    
  def create(self, provider: str):
    
    if provider == LLMEnums.OPENAI.value:
      from .providers import OpenAIProvider
      return OpenAIProvider(
        api_key=self.config.OPENAI_API_KEY,
        api_url=self.config.OPENAI_API_URL,
        default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
        default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
        max_retries=self.config.MAX_RETRIES,
      )
    
    if provider == LLMEnums.COHERE.value:
      from .providers import CoHereProvider
      return CoHereProvider(
        api_key=self.config.COHERE_API_KEY,
        default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
        default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
        max_retries=self.config.MAX_RETRIES,
      )
    
    if provider == LLMEnums.GEMINI.value:
      from .providers import GeminiProvider
      return GeminiProvider(
        api_key= self.config.GEMINI_API_KEY,
        default_input_max_characters= self.config.DEFAULT_INPUT_MAX_CHARACHTERS,
        default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
        default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
        max_retries=self.config.MAX_RETRIES,
      )
    
    if provider == LLMEnums.OLLAMA.value:
      from .providers import OllamaProvider
      return OllamaProvider(
        api_key=self.config.OLLAMA_API_KEY,
        default_input_max_characters= self.config.DEFAULT_INPUT_MAX_CHARACHTERS,
        default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
        default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
        max_retries=self.config.MAX_RETRIES,
      )

    return None
  

class AsyncLLMProviderFactory:
  
  def __init__(self, config: dict):
    self.config = config
    
  def create(self, provider: str):
  
    if provider == LLMEnums.OPENAI.value:
      from .providers import AsyncOpenAIProvider
      return AsyncOpenAIProvider(
        api_key=self.config.OPENAI_API_KEY,
        api_url=self.config.OPENAI_API_URL,
        default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
        default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
        max_retries=self.config.MAX_RETRIES,
      )
    
    if provider == LLMEnums.COHERE.value:
      from .providers import AsyncCoHereProvider
      return AsyncCoHereProvider(
        api_key=self.config.COHERE_API_KEY,
        default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
        default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
        max_retries=self.config.MAX_RETRIES,
      )
    
    if provider == LLMEnums.GEMINI.value:
      from .providers import AsyncGeminiProvider
      return AsyncGeminiProvider(
        api_key= self.config.GEMINI_API_KEY,
        default_input_max_characters= self.config.DEFAULT_INPUT_MAX_CHARACHTERS,
        default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
        default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
        max_retries=self.config.MAX_RETRIES,
      )
    
    if provider == LLMEnums.OLLAMA.value:
      from .providers import AsyncOllamaProvider
      return AsyncOllamaProvider(
        api_key=self.config.OLLAMA_API_KEY,
        api_url=self.config.OLLAMA_HOST_URL,
        default_input_max_characters= self.config.DEFAULT_INPUT_MAX_CHARACHTERS,
        default_generation_max_output_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
        default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
        max_retries=self.config.MAX_RETRIES,
      )

    return None