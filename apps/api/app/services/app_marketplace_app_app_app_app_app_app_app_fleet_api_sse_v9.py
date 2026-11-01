"""Fleet API SSE v9 — track Server-Sent Events streaming connections."""
from __future__ import annotations
def fleet_api_sse_v9(streams: list[dict]) -> dict:
    active = [s for s in streams if s.get("active")]
    connections = sum(s.get("connections", 0) for s in streams)
    events_sec = sum(s.get("events_per_sec", 0) for s in streams)
    return {"streams": len(streams), "active": len(active), "connections": connections,
            "events_per_sec": events_sec, "healthy": True}
