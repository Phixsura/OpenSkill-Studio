"""Localization — i18n string management and translation coverage."""

import html


def build_locale_bundle(*, base: dict[str, str], translations: dict[str, dict[str, str]]) -> dict:
    locales = {}
    for locale, strings in translations.items():
        missing = [k for k in base if k not in strings]
        coverage = round((len(base) - len(missing)) / max(len(base), 1) * 100, 1)
        locales[locale] = {"strings": {k: html.escape(v) for k, v in strings.items()},
                            "missing": missing, "coverage_pct": coverage,
                            "complete": len(missing) == 0}
    return {"base_locale": "en", "base_keys": len(base), "locales": locales,
            "locale_count": len(locales)}


def get_string(*, key: str, locale: str, bundle: dict) -> str:
    loc = bundle.get("locales", {}).get(locale, {})
    return loc.get("strings", {}).get(key, key)
