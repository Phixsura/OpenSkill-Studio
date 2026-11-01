"""Internationalization — manage i18n strings and locale bundles for apps."""

import json


def create_locale_bundle(*, app_id: str, locale: str, strings: dict[str, str]) -> dict:
    if not locale or len(locale) < 2:
        return {"error": "Invalid locale code"}
    return {"app_id": app_id, "locale": locale, "string_count": len(strings),
            "strings": strings, "error": None}


def get_translated_string(*, key: str, locale: str, bundles: dict[str, dict[str, str]],
                             fallback_locale: str = "en") -> str:
    bundle = bundles.get(locale, {})
    if key in bundle:
        return bundle[key]
    fallback = bundles.get(fallback_locale, {})
    return fallback.get(key, key)


def compute_translation_completeness(*, base_keys: list[str], translated_keys: list[str]) -> dict:
    base_set = set(base_keys)
    translated_set = set(translated_keys)
    missing = sorted(base_set - translated_set)
    extra = sorted(translated_set - base_set)
    pct = round(len(translated_set & base_set) / max(len(base_set), 1) * 100, 1)
    return {"completeness_pct": pct, "missing": missing, "extra": extra,
            "missing_count": len(missing), "complete": len(missing) == 0}


def merge_locale_bundles(*, base: dict[str, str], override: dict[str, str]) -> dict[str, str]:
    merged = dict(base)
    merged.update(override)
    return merged
