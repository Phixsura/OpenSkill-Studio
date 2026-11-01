"""Localization — manage app listing translations."""

SUPPORTED_LOCALES = {"en", "zh", "ja", "ko", "es", "fr", "de", "pt"}


def add_translation(*, app_id: str, locale: str, fields: dict) -> dict:
    if locale not in SUPPORTED_LOCALES:
        return {"error": f"Unsupported locale: {locale}. Supported: {', '.join(sorted(SUPPORTED_LOCALES))}"}
    translatable = {"name", "description", "short_description", "changelog"}
    invalid = set(fields.keys()) - translatable
    if invalid:
        return {"error": f"Non-translatable fields: {', '.join(sorted(invalid))}"}
    return {"app_id": app_id, "locale": locale, "fields": fields, "error": None}


def get_localized_listing(*, app: dict, translations: dict, locale: str) -> dict:
    t = translations.get(locale, {})
    return {
        "name": t.get("name", app.get("name", "")),
        "description": t.get("description", app.get("description", "")),
        "short_description": t.get("short_description", app.get("short_description", "")),
        "locale": locale if locale in translations else "en",
        "is_translated": locale in translations,
    }


def get_translation_coverage(*, translations: dict) -> dict:
    coverage = {}
    for locale in SUPPORTED_LOCALES:
        if locale in translations:
            fields = translations[locale]
            coverage[locale] = {"translated": True, "field_count": len(fields)}
        else:
            coverage[locale] = {"translated": False, "field_count": 0}
    translated = sum(1 for v in coverage.values() if v["translated"])
    return {"coverage": coverage, "translated_count": translated, "total_locales": len(SUPPORTED_LOCALES)}
