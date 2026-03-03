from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel
from .locales.PromptTemplate import PromptTemplate
import os
import importlib


class TemplateParserInterface(ABC):

  @abstractmethod
  def get(self, group: str, key: str, vars: dict = {}) -> Optional[str]: ...


class LanguageResolverInterface(ABC):

  @abstractmethod
  def resolve(self, language: Optional[str]) -> str: ...


class PromptTemplateParserInterface:

  @abstractmethod
  def get(self, group: str, key: str, vars: dict = {}) -> Optional[tuple[str, str, type[BaseModel]]]: ...


class FileSystemLanguageResolver(LanguageResolverInterface):

  def __init__(self, base_path: str, default_language: str = "en"):
    self.base_path = base_path
    self.default_language = default_language

  def resolve(self, language: Optional[str]) -> str:
    if not language:
        return self.default_language
    language_path = os.path.join(self.base_path, "locales", language)
    return language if os.path.exists(language_path) else self.default_language


class TemplateParser(TemplateParserInterface):

  def __init__(
    self,
    language: Optional[str] = None,
    default_language: str = "en",
    language_resolver: Optional[LanguageResolverInterface] = None,
  ):
    self.current_path = os.path.dirname(os.path.abspath(__file__))
    self.default_language = default_language
    self.language_resolver = language_resolver or FileSystemLanguageResolver(self.current_path, default_language)
    self.language = self.language_resolver.resolve(language)

  def get(self, group: str, key: str, vars: dict = {}) -> Optional[str]:
    if not group or not key:
      return None

    targeted_language = self.language
    group_path = os.path.join(self.current_path, "locales", targeted_language, f"{group}.py")
    if not os.path.exists(group_path):
      targeted_language = self.default_language
      group_path = os.path.join(self.current_path, "locales", targeted_language, f"{group}.py")

    if not os.path.exists(group_path):
      return None

    module = importlib.import_module(f"stores.llm.templates.locales.{targeted_language}.{group}")
    key_attribute = getattr(module, key, None)
    return key_attribute.substitute(vars) if key_attribute else None

  
class PromptTemplateParser(PromptTemplateParserInterface):

  def __init__(
    self,
    domain: str,
    language: str,
    default_language: str = "en",
    language_resolver: Optional[LanguageResolverInterface] = None,
  ):
    self.current_path = os.path.dirname(os.path.abspath(__file__))
    self.domain = domain
    self.default_language = default_language
    self.language_resolver = language_resolver or FileSystemLanguageResolver(self.current_path, default_language)
    self.language = self.language_resolver.resolve(language)

  def get(self, group: str, key: str, vars: dict = {}) -> Optional[tuple[str, str, type[BaseModel]]]:
    if not group or not key:
      return None

    targeted_language = self.language
    group_path = os.path.join(self.current_path, "locales", targeted_language, self.domain, f"{group}.py")
    if not os.path.exists(group_path):
      targeted_language = self.default_language
      group_path = os.path.join(self.current_path, "locales", targeted_language, self.domain, f"{group}.py")

    if not os.path.exists(group_path):
      return None

    import_path = (
      f"stores.llm.templates.locales.{targeted_language}.{self.domain}.{group}"
      if self.domain else
      f"stores.llm.templates.locales.{targeted_language}.{group}"
    )
    module = importlib.import_module(import_path)
    key_attribute: Optional[PromptTemplate] = getattr(module, key, None)
    
    if key_attribute is None:
      return None
    
    system_message = key_attribute.system.substitute(vars)
    user_message = key_attribute.user.substitute(vars)
    return system_message, user_message, key_attribute.response_model