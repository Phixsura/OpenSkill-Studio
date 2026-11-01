"""Fleet AI Model Deprecation — track model sunset and migration planning."""
from __future__ import annotations
def fleet_ai_model_deprecation(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    deprecated = sum(m.get("deprecated", 0) for m in managers)
    migrated = sum(m.get("migrated", 0) for m in managers)
    sunset_days = min((m.get("sunset_days", 9999) for m in managers), default=9999)
    return {"managers": len(managers), "active": len(active), "deprecated": deprecated,
            "migrated": migrated, "sunset_days": sunset_days, "planned": sunset_days < 9999}
