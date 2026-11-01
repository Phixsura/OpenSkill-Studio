"""Fleet AI Model Cost Tracker — track per-model inference cost."""
from __future__ import annotations
def fleet_ai_model_cost(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    models = sum(t.get("models", 0) for t in trackers)
    total_cost_24h = round(sum(t.get("cost_usd", 0) for t in trackers), 2)
    cost_per_1k = round(sum(t.get("cost_per_1k", 0) for t in trackers) / max(len(trackers), 1), 4)
    return {"trackers": len(trackers), "active": len(active), "models": models,
            "cost_usd": total_cost_24h, "cost_per_1k": cost_per_1k, "tracked": total_cost_24h > 0}
