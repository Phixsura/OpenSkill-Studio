"""Fleet AI Model Scoring — track unified model quality scoring."""
from __future__ import annotations
def fleet_ai_model_scoring(scorers: list[dict]) -> dict:
    active = [s for s in scorers if s.get("active", True)]
    models_scored = sum(s.get("models", 0) for s in scorers)
    avg_score = round(sum(s.get("avg_score", 0) for s in scorers) / max(len(scorers), 1), 1)
    dimensions = sum(s.get("dimensions", 0) for s in scorers)
    return {"scorers": len(scorers), "active": len(active), "models": models_scored,
            "avg_score": avg_score, "dimensions": dimensions, "comprehensive": dimensions > 5}
