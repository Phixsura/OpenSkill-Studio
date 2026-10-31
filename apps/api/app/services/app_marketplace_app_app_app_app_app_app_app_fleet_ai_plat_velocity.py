"""Fleet AI Platform Velocity — track engineering velocity and throughput."""
from __future__ import annotations
def fleet_ai_platform_velocity(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    commits_week = sum(t.get("commits_week", 0) for t in trackers)
    prs_merged_week = sum(t.get("prs_week", 0) for t in trackers)
    cycle_time_h = round(sum(t.get("cycle_time_h", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "commits_week": commits_week,
            "prs_week": prs_merged_week, "cycle_time_h": cycle_time_h, "fast": cycle_time_h < 24}
