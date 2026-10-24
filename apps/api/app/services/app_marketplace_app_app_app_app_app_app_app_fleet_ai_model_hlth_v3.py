"""Fleet AI Model Health v3 — track comprehensive model health scoring."""
from __future__ import annotations
def fleet_ai_model_health_v3(checkers: list[dict]) -> dict:
    active = [c for c in checkers if c.get("active", True)]
    models = sum(c.get("models", 0) for c in checkers)
    health_score = round(sum(c.get("score", 0) for c in checkers) / max(len(checkers), 1), 1)
    degraded = sum(c.get("degraded", 0) for c in checkers)
    dimensions = sum(c.get("dimensions", 0) for c in checkers)
    return {"checkers": len(checkers), "active": len(active), "models": models,
            "score": health_score, "degraded": degraded, "dimensions": dimensions, "green": degraded == 0}
