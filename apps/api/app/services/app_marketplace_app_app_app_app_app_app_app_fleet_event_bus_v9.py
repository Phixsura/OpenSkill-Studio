"""Fleet Event Bus v9 — track event-driven architecture message flow."""
from __future__ import annotations
def fleet_event_bus_v9(topics: list[dict]) -> dict:
    active = [t for t in topics if t.get("active", True)]
    events = sum(t.get("events_per_sec", 0) for t in topics)
    subscribers = sum(t.get("subscribers", 0) for t in topics)
    return {"topics": len(topics), "active": len(active), "events_per_sec": events,
            "total_subscribers": subscribers, "healthy": len(active) == len(topics)}
