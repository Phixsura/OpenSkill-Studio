"""User preference — manage user-level platform preferences."""


DEFAULT_PREFERENCES = {
    "theme": {"value": "system", "options": ["light", "dark", "system"], "category": "appearance"},
    "language": {"value": "en", "options": ["en", "es", "fr", "de", "ja", "zh"], "category": "localization"},
    "timezone": {"value": "UTC", "options": None, "category": "localization"},
    "email_digest": {"value": "weekly", "options": ["daily", "weekly", "monthly", "never"], "category": "notifications"},
    "compact_view": {"value": False, "options": [True, False], "category": "appearance"},
    "code_font_size": {"value": 14, "options": [12, 14, 16, 18, 20], "category": "editor"},
    "auto_save": {"value": True, "options": [True, False], "category": "editor"},
}


def get_preferences(*, overrides: dict | None = None) -> dict:
    prefs = {}
    for key, default in DEFAULT_PREFERENCES.items():
        value = (overrides or {}).get(key, default["value"])
        prefs[key] = {**default, "value": value, "is_default": value == default["value"]}
    categories = sorted(set(p["category"] for p in prefs.values()))
    return {"preferences": prefs, "categories": categories, "total": len(prefs)}


def update_preference(*, key: str, value) -> dict:
    if key not in DEFAULT_PREFERENCES:
        return {"error": f"Unknown preference: {key}"}
    opts = DEFAULT_PREFERENCES[key].get("options")
    if opts is not None and value not in opts:
        return {"error": f"Invalid value. Options: {opts}"}
    return {"key": key, "value": value, "updated": True}
