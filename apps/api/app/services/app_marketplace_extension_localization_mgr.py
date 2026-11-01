"""Extension Localization Manager — multi-language support for listings."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class LocalizedContent:
    locale: str  # e.g. en, zh, ja, ko, fr, de, es
    name: str = ""
    tagline: str = ""
    description: str = ""


class ExtLocalizationMgrService:
    SUPPORTED_LOCALES = {"en", "zh", "ja", "ko", "fr", "de", "es", "pt", "ru", "ar"}

    def __init__(self):
        self._content: dict[str, dict[str, LocalizedContent]] = {}  # ext_id -> locale -> content

    def set(self, extension_id: str, locale: str, name: str = "",
            tagline: str = "", description: str = "") -> LocalizedContent:
        if locale not in self.SUPPORTED_LOCALES:
            raise ValueError(f"Unsupported locale: {locale}")
        if extension_id not in self._content:
            self._content[extension_id] = {}
        lc = LocalizedContent(locale=locale, name=name, tagline=tagline, description=description)
        self._content[extension_id][locale] = lc
        return lc

    def get(self, extension_id: str, locale: str, fallback: str = "en") -> LocalizedContent | None:
        ext_content = self._content.get(extension_id, {})
        return ext_content.get(locale) or ext_content.get(fallback)

    def get_locales(self, extension_id: str) -> list[str]:
        return list(self._content.get(extension_id, {}).keys())

    def get_completeness(self, extension_id: str) -> dict[str, float]:
        ext_content = self._content.get(extension_id, {})
        result = {}
        for locale, lc in ext_content.items():
            fields = [lc.name, lc.tagline, lc.description]
            filled = sum(1 for f in fields if f)
            result[locale] = round(filled / 3 * 100)
        return result
