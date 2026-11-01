"""Fleet AI Experiments — track A/B testing for AI models."""
from __future__ import annotations
def fleet_ai_experiments(experiments: list[dict]) -> dict:
    active = [e for e in experiments if e.get("active", True)]
    variants = sum(e.get("variants", 0) for e in experiments)
    traffic_pct = round(sum(e.get("traffic_pct", 0) for e in active) / max(len(active), 1), 1)
    return {"total": len(experiments), "active": len(active), "variants": variants,
            "avg_traffic_pct": traffic_pct, "running": len(active) > 0}
