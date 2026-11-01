"""Fleet AI Release Manager — track AI model release coordination."""
from __future__ import annotations
def fleet_ai_release_manager(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    releases_24h = sum(m.get("releases_24h", 0) for m in managers)
    rollbacks = sum(m.get("rollbacks", 0) for m in managers)
    lead_time_min = round(sum(m.get("lead_time_min", 0) for m in managers) / max(len(managers), 1), 1)
    return {"managers": len(managers), "active": len(active), "releases_24h": releases_24h,
            "rollbacks": rollbacks, "lead_time_min": lead_time_min, "fast": lead_time_min < 30}
