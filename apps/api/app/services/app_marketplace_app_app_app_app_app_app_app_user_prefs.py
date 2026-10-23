"""User preferences — per-user settings with defaults and persistence."""
from __future__ import annotations

DEFAULTS = {
    "theme": "system", "language": "en", "timezone": "UTC",
    "notifications_email": True, "notifications_push": True,
    "sidebar_collapsed": False, "density": "comfortable",
    "date_format": "YYYY-MM-DD", "code_font_size": 14,
}


def get_prefs(user_id: str, overrides: dict | None = None) -> dict:
    prefs = dict(DEFAULTS)
    if overrides:
        prefs.update(overrides)
    return {"user_id": user_id, "preferences": prefs}


def update_pref(current: dict, key: str, value) -> dict:
    if key not in DEFAULTS:
        return {"error": f"Unknown preference: {key}"}
    expected_type = type(DEFAULTS[key])
    if not isinstance(value, expected_type):
        return {"error": f"{key} expects {expected_type.__name__}"}
    current[key] = value
    return {"updated": key, "value": value}


def reset_prefs() -> dict:
    return {"preferences": dict(DEFAULTS), "reset": True}
