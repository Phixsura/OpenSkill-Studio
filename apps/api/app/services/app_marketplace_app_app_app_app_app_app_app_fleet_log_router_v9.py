"""Fleet Log Router v9 — track log routing rules and destinations."""
from __future__ import annotations
def fleet_log_router_v9(routes: list[dict]) -> dict:
    active = [r for r in routes if r.get("active")]
    destinations = len({r.get("destination") for r in routes if r.get("destination")})
    events_sec = sum(r.get("events_per_sec", 0) for r in routes)
    return {"routes": len(routes), "active": len(active), "destinations": destinations,
            "events_per_sec": events_sec, "healthy": len(active) == len(routes)}
