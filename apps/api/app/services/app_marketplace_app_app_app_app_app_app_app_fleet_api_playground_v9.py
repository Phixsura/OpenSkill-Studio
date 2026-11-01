"""Fleet API Playground v9 — track interactive API playground usage."""
from __future__ import annotations
def fleet_api_playground_v9(playgrounds: list[dict]) -> dict:
    active = [p for p in playgrounds if p.get("active")]
    requests = sum(p.get("requests_today", 0) for p in playgrounds)
    users = len({p.get("user") for p in playgrounds if p.get("user")})
    return {"playgrounds": len(playgrounds), "active": len(active), "requests_today": requests,
            "unique_users": users, "healthy": True}
