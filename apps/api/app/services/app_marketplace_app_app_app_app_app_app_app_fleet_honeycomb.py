"""Fleet Honeycomb — track observability and debugging."""
from __future__ import annotations
def fleet_honeycomb_status(datasets: list[dict]) -> dict:
    active = [d for d in datasets if d.get("active", True)]
    total_events = sum(d.get("events_per_sec", 0) for d in active)
    queries_24h = sum(d.get("queries_24h", 0) for d in datasets)
    return {"datasets": len(datasets), "active": len(active), "events_per_sec": total_events,
            "queries_24h": queries_24h, "well_used": queries_24h > 100}
