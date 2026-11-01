"""User preferences — persist user settings across marketplace sessions."""

DEFAULT_PREFERENCES = {
    "theme": "system",
    "view_mode": "grid",
    "per_page": 24,
    "sort_by": "popular",
    "show_previews": True,
    "email_digest": "weekly",
    "language": "en",
    "timezone": "UTC",
}


def get_preferences(*, stored: dict | None = None) -> dict:
    prefs = dict(DEFAULT_PREFERENCES)
    if stored:
        prefs.update(stored)
    return prefs


def update_preference(*, current: dict, key: str, value: object) -> dict:
    if key not in DEFAULT_PREFERENCES:
        return {**current, "_error": f"Unknown preference: {key}"}
    updated = dict(current)
    updated[key] = value
    return updated


def reset_preferences() -> dict:
    return dict(DEFAULT_PREFERENCES)


def get_preference_schema() -> list[dict]:
    return [
        {"key": "theme", "label": "Theme", "type": "select", "options": ["system", "light", "dark"]},
        {"key": "view_mode", "label": "View Mode", "type": "select", "options": ["grid", "list"]},
        {"key": "per_page", "label": "Items Per Page", "type": "select", "options": [12, 24, 48]},
        {"key": "sort_by", "label": "Default Sort", "type": "select", "options": ["popular", "rating", "newest", "name"]},
        {"key": "show_previews", "label": "Show Previews", "type": "boolean"},
        {"key": "email_digest", "label": "Email Digest", "type": "select", "options": ["daily", "weekly", "monthly", "never"]},
    ]
