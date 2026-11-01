"""Fleet Trigger.dev — track background job platform."""
from __future__ import annotations
def fleet_triggerdev_status(projects: list[dict]) -> dict:
    active = [p for p in projects if p.get("active", True)]
    runs_24h = sum(p.get("runs_24h", 0) for p in projects)
    tasks = sum(p.get("tasks", 0) for p in projects)
    return {"projects": len(projects), "active": len(active), "runs_24h": runs_24h,
            "tasks": tasks, "productive": runs_24h > 1000}
