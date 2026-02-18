import os
from enum import Enum

_LOCALES_PATH = os.path.dirname(__file__)
print(_LOCALES_PATH)

def _get_supported_languages():
    return {
        lang.upper(): lang for lang in os.listdir(_LOCALES_PATH)
        if os.path.isdir(os.path.join(_LOCALES_PATH, lang))
    }

def get_supported_domains(language: str) -> list[str]:
    lang_path = os.path.join(_LOCALES_PATH, language)
    if not os.path.isdir(lang_path):
        return []
    return [
        name for name in os.listdir(lang_path)
        if os.path.isdir(os.path.join(lang_path, name))
    ]

class SupportedLanguage(str, Enum):
    locals().update(_get_supported_languages())