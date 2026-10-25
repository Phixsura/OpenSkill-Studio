"""Extension i18n — internationalization support for marketplace extensions.

Manages translation bundles, locale detection, fallback chains,
and pluralization for extension UIs and marketplace listings.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class TranslationBundle:
    locale: str  # e.g. "en", "zh-CN", "ja"
    messages: dict[str, str]  # key -> translated string


class ExtensionI18n:
    """Manages translations for extension marketplace content."""

    def __init__(self, default_locale: str = "en"):
        self._default = default_locale
        self._bundles: dict[str, dict[str, TranslationBundle]] = {}  # ext -> locale -> bundle
        self._fallback_chain: dict[str, str] = {
            "zh-TW": "zh-CN", "zh-CN": "en", "ja": "en", "ko": "en",
            "fr": "en", "de": "en", "es": "en", "pt-BR": "pt",
            "pt": "en",
        }

    def register_bundle(self, extension_id: str, bundle: TranslationBundle) -> None:
        self._bundles.setdefault(extension_id, {})[bundle.locale] = bundle

    def get_message(self, extension_id: str, key: str, locale: str = "",
                    params: dict[str, str] | None = None) -> str:
        """Get a translated message with fallback and parameter interpolation."""
        locale = locale or self._default
        message = self._resolve(extension_id, key, locale)
        if message and params:
            for k, v in params.items():
                message = message.replace(f"{{{k}}}", v)
        return message or key  # return key as fallback

    def _resolve(self, extension_id: str, key: str, locale: str) -> str | None:
        bundles = self._bundles.get(extension_id, {})
        # Try exact locale
        bundle = bundles.get(locale)
        if bundle and key in bundle.messages:
            return bundle.messages[key]
        # Try fallback chain
        fallback = self._fallback_chain.get(locale)
        if fallback:
            return self._resolve(extension_id, key, fallback)
        # Try default locale
        if locale != self._default:
            default_bundle = bundles.get(self._default)
            if default_bundle and key in default_bundle.messages:
                return default_bundle.messages[key]
        return None

    def get_supported_locales(self, extension_id: str) -> list[str]:
        return sorted(self._bundles.get(extension_id, {}).keys())

    def get_translation_coverage(self, extension_id: str, locale: str) -> dict:
        """Check how complete a locale's translations are vs default."""
        bundles = self._bundles.get(extension_id, {})
        default_bundle = bundles.get(self._default)
        target_bundle = bundles.get(locale)
        if not default_bundle:
            return {"locale": locale, "coverage": 0, "total": 0, "translated": 0}
        total = len(default_bundle.messages)
        translated = len(target_bundle.messages) if target_bundle else 0
        return {
            "locale": locale,
            "total": total,
            "translated": translated,
            "missing": total - translated,
            "coverage": round(translated / max(1, total) * 100, 1),
        }

    def export_bundle(self, extension_id: str, locale: str) -> dict[str, str]:
        bundle = self._bundles.get(extension_id, {}).get(locale)
        return dict(bundle.messages) if bundle else {}
