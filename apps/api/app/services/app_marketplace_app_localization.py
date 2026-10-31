"""App localization — manage translations for app listings."""


SUPPORTED_LOCALES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "ja": "Japanese", "ko": "Korean", "zh": "Chinese", "pt": "Portuguese",
}


def get_localization_status(*, app_id: str, translations: dict[str, dict]) -> dict:
    status = []
    for locale, name in SUPPORTED_LOCALES.items():
        t = translations.get(locale, {})
        fields = ["title", "description", "screenshots", "changelog"]
        completed = sum(1 for f in fields if t.get(f))
        status.append({
            "locale": locale, "language": name,
            "completed_fields": completed, "total_fields": len(fields),
            "progress": round(completed / len(fields) * 100),
            "is_default": locale == "en",
        })
    total_pct = round(sum(s["progress"] for s in status) / len(status))
    return {"app_id": app_id, "locales": status,
            "overall_progress": total_pct, "supported_count": len(SUPPORTED_LOCALES)}


def validate_translation(*, locale: str, title: str, description: str) -> dict:
    if locale not in SUPPORTED_LOCALES:
        return {"valid": False, "error": f"Unsupported locale: {locale}"}
    errors = []
    if len(title) < 3:
        errors.append("Title too short (min 3 chars)")
    if len(title) > 100:
        errors.append("Title too long (max 100 chars)")
    if len(description) < 20:
        errors.append("Description too short (min 20 chars)")
    return {"valid": len(errors) == 0, "errors": errors, "locale": locale}
