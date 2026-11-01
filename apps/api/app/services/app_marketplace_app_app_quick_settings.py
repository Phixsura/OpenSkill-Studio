"""Quick settings — commonly used app settings in one place."""


DEFAULT_SETTINGS = {
    "auto_update": {"value": True, "type": "boolean", "label": "Auto-update enabled", "category": "general"},
    "notifications": {"value": True, "type": "boolean", "label": "Push notifications", "category": "general"},
    "dark_mode": {"value": "system", "type": "select", "label": "Theme", "options": ["light", "dark", "system"], "category": "appearance"},
    "language": {"value": "en", "type": "select", "label": "Language", "options": ["en", "es", "fr", "de", "ja"], "category": "localization"},
    "analytics_opt_in": {"value": True, "type": "boolean", "label": "Share usage analytics", "category": "privacy"},
    "crash_reports": {"value": True, "type": "boolean", "label": "Send crash reports", "category": "privacy"},
}


def get_quick_settings(*, overrides: dict | None = None) -> dict:
    settings = {}
    for key, default in DEFAULT_SETTINGS.items():
        value = (overrides or {}).get(key, default["value"])
        settings[key] = {**default, "value": value, "modified": value != default["value"]}
    categories = sorted(set(s["category"] for s in settings.values()))
    modified_count = sum(1 for s in settings.values() if s["modified"])
    return {"settings": settings, "categories": categories,
            "total": len(settings), "modified_count": modified_count}


def reset_setting(*, key: str) -> dict:
    if key not in DEFAULT_SETTINGS:
        return {"error": f"Unknown setting: {key}"}
    return {"key": key, "value": DEFAULT_SETTINGS[key]["value"], "reset": True}
