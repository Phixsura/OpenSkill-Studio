"""Fleet Segment — track customer data platform."""
from __future__ import annotations
def fleet_segment_status(workspaces: list[dict]) -> dict:
    active = [w for w in workspaces if w.get("active", True)]
    events_24h = sum(w.get("events_24h", 0) for w in workspaces)
    sources = sum(w.get("sources", 0) for w in workspaces)
    destinations = sum(w.get("destinations", 0) for w in workspaces)
    return {"workspaces": len(workspaces), "active": len(active), "events_24h": events_24h,
            "sources": sources, "destinations": destinations}
