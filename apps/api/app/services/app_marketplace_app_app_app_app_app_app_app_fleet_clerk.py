"""Fleet Clerk — track modern auth platform health."""
from __future__ import annotations
def fleet_clerk_status(apps: list[dict]) -> dict:
    active = [a for a in apps if a.get("active", True)]
    total_users = sum(a.get("users", 0) for a in apps)
    sessions_24h = sum(a.get("sessions_24h", 0) for a in apps)
    return {"apps": len(apps), "active": len(active), "users": total_users,
            "sessions_24h": sessions_24h, "all_active": len(active) == len(apps)}
