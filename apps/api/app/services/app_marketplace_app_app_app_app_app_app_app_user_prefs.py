"""User preference store — persist user preferences."""
from __future__ import annotations

_prefs: dict[str, dict] = {}

DEFAULTS = {"theme": "system", "language": "en", "email_digest": "weekly",
            "show_tips": True, "compact_view": False, "timezone": "UTC"}


def get_prefs(user_id: str) -> dict:
    user_prefs = _prefs.get(user_id, {})
    merged = {**DEFAULTS, **user_prefs}
    return {"user_id": user_id, "preferences": merged,
            "customized": len(user_prefs), "total": len(merged)}


def set_pref(user_id: str, key: str, value: object) -> dict:
    if key not in DEFAULTS:
        return {"set": False, "error": "unknown_preference"}
    _prefs.setdefault(user_id, {})[key] = value
    return {"set": True, "key": key, "value": value}


def reset_prefs(user_id: str) -> dict:
    if user_id in _prefs:
        del _prefs[user_id]
    return {"reset": True, "user_id": user_id}


def clear_all_prefs() -> None:
    _prefs.clear()
