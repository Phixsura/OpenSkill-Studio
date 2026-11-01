"""Fleet Maintenance Window v9 — track planned maintenance windows."""
from __future__ import annotations
def fleet_maintenance_window_v9(windows: list[dict]) -> dict:
    upcoming = [w for w in windows if w.get("status") == "upcoming"]
    in_progress = [w for w in windows if w.get("status") == "in_progress"]
    completed = [w for w in windows if w.get("status") == "completed"]
    return {"windows": len(windows), "upcoming": len(upcoming), "in_progress": len(in_progress),
            "completed": len(completed), "healthy": len(in_progress) == 0}
