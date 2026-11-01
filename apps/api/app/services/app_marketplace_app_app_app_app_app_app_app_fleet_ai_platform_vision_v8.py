"""Fleet AI Vision v8 — track ultimate long-term platform strategy."""
from __future__ import annotations
def fleet_ai_vision_v8(planners: list[dict]) -> dict:
    active = [p for p in planners if p.get("active", True)]
    goals = sum(p.get("goals", 0) for p in planners)
    achieved = sum(p.get("achieved", 0) for p in planners)
    horizon = max((p.get("years", 0) for p in planners), default=0)
    return {"planners": len(planners), "active": len(active), "goals": goals,
            "achieved": achieved, "horizon": horizon, "visionary": horizon >= 5}
