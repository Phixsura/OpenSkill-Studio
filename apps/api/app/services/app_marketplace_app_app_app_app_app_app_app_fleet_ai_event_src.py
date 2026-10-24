"""Fleet AI Event Sourcing — track AI event-driven state management."""
from __future__ import annotations
def fleet_ai_event_sourcing(stores: list[dict]) -> dict:
    active = [s for s in stores if s.get("active", True)]
    events_24h = sum(s.get("events_24h", 0) for s in stores)
    streams = sum(s.get("streams", 0) for s in stores)
    projections = sum(s.get("projections", 0) for s in stores)
    return {"stores": len(stores), "active": len(active), "events_24h": events_24h,
            "streams": streams, "projections": projections, "sourced": events_24h > 0}
