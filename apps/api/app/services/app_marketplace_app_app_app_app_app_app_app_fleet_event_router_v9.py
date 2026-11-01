"""Fleet Event Router v9 — track event-driven routing and fan-out."""
from __future__ import annotations
def fleet_event_router_v9(routes: list[dict]) -> dict:
    active = [r for r in routes if r.get("active")]
    events_sec = sum(r.get("events_per_sec", 0) for r in routes)
    targets = sum(r.get("targets", 0) for r in routes)
    return {"routes": len(routes), "active": len(active), "events_per_sec": events_sec,
            "total_targets": targets, "healthy": len(active) == len(routes)}
