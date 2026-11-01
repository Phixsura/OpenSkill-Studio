"""App data retention settings — configure how long app data is kept."""
from __future__ import annotations

RETENTION_PRESETS = {
    "minimal": {"logs": 7, "analytics": 30, "user_data": 90, "backups": 30},
    "standard": {"logs": 30, "analytics": 90, "user_data": 365, "backups": 90},
    "extended": {"logs": 90, "analytics": 365, "user_data": 730, "backups": 365},
    "compliance": {"logs": 365, "analytics": 730, "user_data": 2555, "backups": 730},
}


def get_retention_preset(preset: str) -> dict:
    config = RETENTION_PRESETS.get(preset, RETENTION_PRESETS["standard"])
    return {"preset": preset, "config": config,
            "total_categories": len(config),
            "display": {k: f"{v} days" for k, v in config.items()}}


def validate_retention(config: dict) -> dict:
    errors = []
    for key, days in config.items():
        if days < 1:
            errors.append(f"{key}: minimum 1 day")
        if key == "user_data" and days < 30:
            errors.append("user_data: GDPR requires minimum 30 days for deletion requests")
    return {"valid": len(errors) == 0, "errors": errors}


def list_presets() -> list[dict]:
    return [{"id": k, "label": k.capitalize(),
             "max_days": max(v.values())} for k, v in RETENTION_PRESETS.items()]
