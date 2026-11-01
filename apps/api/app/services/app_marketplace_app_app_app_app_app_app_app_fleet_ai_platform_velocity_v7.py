"""Fleet AI Velocity v7 — track ultimate engineering velocity."""
from __future__ import annotations
def fleet_ai_velocity_v7(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    commits_week = sum(t.get("commits", 0) for t in trackers)
    prs_week = sum(t.get("prs", 0) for t in trackers)
    cycle_h = round(sum(t.get("cycle_h", 0) for t in trackers) / max(len(trackers), 1), 1)
    throughput = sum(t.get("features_week", 0) for t in trackers)
    return {"trackers": len(trackers), "active": len(active), "commits": commits_week,
            "prs": prs_week, "cycle_h": cycle_h, "features": throughput, "fast": cycle_h < 24}
