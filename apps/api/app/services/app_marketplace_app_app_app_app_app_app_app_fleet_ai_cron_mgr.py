"""Fleet AI Cron Manager — track periodic AI job scheduling."""
from __future__ import annotations
def fleet_ai_cron_manager(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    jobs = sum(m.get("jobs", 0) for m in managers)
    runs_24h = sum(m.get("runs_24h", 0) for m in managers)
    missed = sum(m.get("missed", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "jobs": jobs,
            "runs_24h": runs_24h, "missed": missed, "punctual": missed == 0}
