"""Fleet AI Platform Capacity v3 — track predictive capacity management."""
from __future__ import annotations
def fleet_ai_platform_capacity_v3(planners: list[dict]) -> dict:
    active = [p for p in planners if p.get("active", True)]
    forecasts = sum(p.get("forecasts", 0) for p in planners)
    accuracy = round(sum(p.get("accuracy_pct", 0) for p in planners) / max(len(planners), 1), 1)
    headroom = round(sum(p.get("headroom_pct", 0) for p in planners) / max(len(planners), 1), 1)
    return {"planners": len(planners), "active": len(active), "forecasts": forecasts,
            "accuracy": accuracy, "headroom": headroom, "prepared": headroom > 20}
