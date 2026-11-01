"""Fleet AI Model Access Log — track who accessed which models when."""
from __future__ import annotations
def fleet_ai_model_access_log(loggers: list[dict]) -> dict:
    active = [l for l in loggers if l.get("active", True)]
    accesses_24h = sum(l.get("accesses_24h", 0) for l in loggers)
    unique_users = sum(l.get("users", 0) for l in loggers)
    models_accessed = sum(l.get("models", 0) for l in loggers)
    return {"loggers": len(loggers), "active": len(active), "accesses_24h": accesses_24h,
            "users": unique_users, "models": models_accessed, "auditable": accesses_24h > 0}
