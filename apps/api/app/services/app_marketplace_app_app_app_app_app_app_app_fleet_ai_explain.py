"""Fleet AI Explainability — track model interpretability."""
from __future__ import annotations
def fleet_ai_explainability(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    explanations_24h = sum(s.get("explanations_24h", 0) for s in services)
    models_covered = sum(s.get("models", 0) for s in services)
    return {"services": len(services), "active": len(active), "explanations_24h": explanations_24h,
            "models": models_covered, "transparent": len(active) == len(services)}
