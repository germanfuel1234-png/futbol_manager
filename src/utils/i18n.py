"""
Sistema de internacionalización (i18n).
Detecta el idioma del sistema y carga el JSON correspondiente.
"""
import json
import locale
import os

_translations: dict = {}
_current_lang: str = "es"

_BASE = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "i18n")


def load_language(lang: str = "es"):
    global _translations, _current_lang
    path = os.path.join(_BASE, f"{lang}.json")
    if not os.path.exists(path):
        lang = "es"
        path = os.path.join(_BASE, "es.json")
    with open(path, encoding="utf-8") as f:
        _translations = json.load(f)
    _current_lang = lang


def t(key: str, **kwargs) -> str:
    """Traducir una clave. Acepta parámetros de formato."""
    text = _translations.get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text


def get_current_lang() -> str:
    return _current_lang


def detect_system_language() -> str:
    """Detecta el idioma del sistema operativo."""
    try:
        lang_code = locale.getdefaultlocale()[0] or "es"
        return "en" if lang_code.startswith("en") else "es"
    except Exception:
        return "es"


def available_languages() -> list[tuple[str, str]]:
    return [("es", "Español"), ("en", "English")]


# Cargar idioma al importar
load_language(detect_system_language())
