"""Fleet AI Platform Vision v7 — track long-term AI platform strategy."""
from __future__ import annotations
def fleet_ai_platform_vision_v7(planners: list[dict]) -> dict:
    active = [p for p in planners if p.get("active", True)]
    goals = sum(p.get("goals", 0) for p in planners)
    achieved = sum(p.get("achieved", 0) for p in planners)
    horizon_years = max((p.get("years", 0) for p in planners), default=0)
    return {"planners": len(planners), "active": len(active), "goals": goals,
            "achieved": achieved, "horizon": horizon_years, "visionary": horizon_years >= 3}
