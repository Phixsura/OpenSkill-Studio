"""Fleet API Event Stream v9 — track event streaming API endpoints."""
from __future__ import annotations
def fleet_api_event_stream_v9(streams: list[dict]) -> dict:
    active = [s for s in streams if s.get("active")]
    consumers = sum(s.get("consumers", 0) for s in streams)
    events_sec = sum(s.get("events_per_sec", 0) for s in streams)
    return {"streams": len(streams), "active": len(active), "consumers": consumers,
            "events_per_sec": events_sec, "healthy": len(active) == len(streams)}
