"""Fleet Novu — track notification infrastructure."""
from __future__ import annotations
def fleet_novu_status(environments: list[dict]) -> dict:
    active = [e for e in environments if e.get("active", True)]
    notifications_24h = sum(e.get("notifications_24h", 0) for e in environments)
    channels = sum(e.get("channels", 0) for e in environments)
    return {"environments": len(environments), "active": len(active), "notifications_24h": notifications_24h,
            "channels": channels, "all_active": len(active) == len(environments)}
