"""Fleet Inngest — track event-driven function platform."""
from __future__ import annotations
def fleet_inngest_status(apps: list[dict]) -> dict:
    active = [a for a in apps if a.get("active", True)]
    functions = sum(a.get("functions", 0) for a in apps)
    events_24h = sum(a.get("events_24h", 0) for a in apps)
    return {"apps": len(apps), "active": len(active), "functions": functions,
            "events_24h": events_24h, "all_active": len(active) == len(apps)}
