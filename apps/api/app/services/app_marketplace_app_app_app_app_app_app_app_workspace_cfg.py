"""Workspace settings — manage workspace-level configuration."""
from __future__ import annotations


DEFAULTS = {
    "theme": "system", "language": "en", "timezone": "UTC",
    "date_format": "YYYY-MM-DD", "notifications_enabled": True,
    "two_factor_required": False, "session_timeout_min": 60,
    "max_api_keys": 10, "audit_log_retention_days": 90,
}


def get_settings(overrides: dict | None = None) -> dict:
    settings = {**DEFAULTS, **(overrides or {})}
    return {"settings": settings, "total": len(settings),
            "customized": len(overrides or {}),
            "using_defaults": len(settings) - len(overrides or {})}


def update_setting(current: dict, key: str, value: object) -> dict:
    if key not in DEFAULTS:
        return {"updated": False, "error": "unknown_setting"}
    old = current.get(key, DEFAULTS.get(key))
    current[key] = value
    return {"updated": True, "key": key, "old_value": old, "new_value": value}


def reset_to_defaults() -> dict:
    return {"settings": {**DEFAULTS}, "reset": True}
