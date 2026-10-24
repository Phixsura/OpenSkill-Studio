"""Fleet AI Playground — track interactive AI experimentation environments."""
from __future__ import annotations
def fleet_ai_playground(playgrounds: list[dict]) -> dict:
    active = [p for p in playgrounds if p.get("active", True)]
    users_24h = sum(p.get("users_24h", 0) for p in playgrounds)
    experiments_24h = sum(p.get("experiments_24h", 0) for p in playgrounds)
    models_available = sum(p.get("models", 0) for p in playgrounds)
    return {"playgrounds": len(playgrounds), "active": len(active), "users_24h": users_24h,
            "experiments_24h": experiments_24h, "models": models_available, "popular": users_24h > 1000}
