"""User preference — user settings and preferences manager."""

import html

DEFAULTS = {
    "theme": "system", "language": "en", "timezone": "UTC",
    "notifications_email": True, "notifications_push": True,
    "notifications_slack": False, "compact_view": False,
    "code_font_size": 14, "sidebar_collapsed": False,
}
THEMES = ["light", "dark", "system"]
LANGUAGES = ["en", "es", "fr", "de", "ja", "zh", "ko", "pt"]


def get_preferences(*, overrides: dict | None = None) -> dict:
    prefs = dict(DEFAULTS)
    if overrides:
        for k, v in overrides.items():
            if k in prefs:
                prefs[k] = v
    return {"preferences": prefs, "available_themes": THEMES,
            "available_languages": LANGUAGES}


def validate_preference(*, key: str, value) -> dict:
    if key not in DEFAULTS:
        return {"valid": False, "error": f"Unknown preference: {key}"}
    expected = type(DEFAULTS[key])
    if not isinstance(value, expected):
        return {"valid": False, "error": f"Expected {expected.__name__}, got {type(value).__name__}"}
    if key == "theme" and value not in THEMES:
        return {"valid": False, "error": f"Theme must be one of: {', '.join(THEMES)}"}
    if key == "language" and value not in LANGUAGES:
        return {"valid": False, "error": f"Language must be one of: {', '.join(LANGUAGES)}"}
    return {"valid": True, "key": key, "value": value}
