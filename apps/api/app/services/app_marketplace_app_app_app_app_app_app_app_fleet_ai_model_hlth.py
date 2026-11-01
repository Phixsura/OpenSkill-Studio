"""Fleet AI Model Health — track individual model health scoring."""
from __future__ import annotations
def fleet_ai_model_health(checkers: list[dict]) -> dict:
    active = [c for c in checkers if c.get("active", True)]
    models_checked = sum(c.get("models", 0) for c in checkers)
    healthy = sum(c.get("healthy", 0) for c in checkers)
    degraded = sum(c.get("degraded", 0) for c in checkers)
    avg_score = round(sum(c.get("score", 0) for c in checkers) / max(len(checkers), 1), 1)
    return {"checkers": len(checkers), "active": len(active), "models": models_checked,
            "healthy": healthy, "degraded": degraded, "score": avg_score, "green": degraded == 0}
