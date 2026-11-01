"""Fleet AI Capacity v5 — track ultimate compute capacity planning."""
from __future__ import annotations
def fleet_ai_capacity_v5(planners: list[dict]) -> dict:
    active = [p for p in planners if p.get("active", True)]
    gpus = sum(p.get("gpus", 0) for p in planners)
    headroom = round(sum(p.get("headroom_pct", 0) for p in planners) / max(len(planners), 1), 1)
    forecast_days = max((p.get("forecast_days", 0) for p in planners), default=0)
    return {"planners": len(planners), "active": len(active), "gpus": gpus,
            "headroom": headroom, "forecast_days": forecast_days, "prepared": headroom > 25}
