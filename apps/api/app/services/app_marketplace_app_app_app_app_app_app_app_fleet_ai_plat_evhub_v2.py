"""Fleet AI Event Hub v2 — track centralized event processing."""
from __future__ import annotations
def fleet_ai_event_hub_v2(hubs: list[dict]) -> dict:
    active = [h for h in hubs if h.get("active", True)]
    events_24h = sum(h.get("events_24h", 0) for h in hubs)
    topics = sum(h.get("topics", 0) for h in hubs)
    consumers = sum(h.get("consumers", 0) for h in hubs)
    return {"hubs": len(hubs), "active": len(active), "events_24h": events_24h,
            "topics": topics, "consumers": consumers, "streaming": events_24h > 0}
