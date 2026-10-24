"""Fleet SSE metrics — track Server-Sent Events."""
from __future__ import annotations
def fleet_sse_metrics(streams: list[dict]) -> dict:
    active = sum(s.get("active_connections", 0) for s in streams)
    events_per_sec = sum(s.get("events_per_sec", 0) for s in streams)
    return {"streams": len(streams), "active_connections": active,
            "events_per_sec": events_per_sec, "high_volume": events_per_sec > 10000}
