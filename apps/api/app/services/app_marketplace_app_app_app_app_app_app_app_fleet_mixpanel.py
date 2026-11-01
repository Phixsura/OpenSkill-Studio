"""Fleet Mixpanel — track product analytics platform."""
from __future__ import annotations
def fleet_mixpanel_status(projects: list[dict]) -> dict:
    active = [p for p in projects if p.get("active", True)]
    events_24h = sum(p.get("events_24h", 0) for p in projects)
    users_tracked = sum(p.get("users", 0) for p in projects)
    return {"projects": len(projects), "active": len(active), "events_24h": events_24h,
            "users": users_tracked, "data_flowing": events_24h > 0}
