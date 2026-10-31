"""Fleet AI Model Warm-Up — track model pre-loading and initialization."""
from __future__ import annotations
def fleet_ai_model_warmup(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    models_warmed = sum(m.get("warmed", 0) for m in managers)
    cold_starts_prevented = sum(m.get("prevented", 0) for m in managers)
    avg_warmup_s = round(sum(m.get("warmup_s", 0) for m in managers) / max(len(managers), 1), 1)
    return {"managers": len(managers), "active": len(active), "warmed": models_warmed,
            "prevented": cold_starts_prevented, "warmup_s": avg_warmup_s, "ready": models_warmed > 0}
