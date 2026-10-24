"""Fleet AI PubSub — track AI event publish-subscribe messaging."""
from __future__ import annotations
def fleet_ai_pubsub(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    topics = sum(s.get("topics", 0) for s in systems)
    subscriptions = sum(s.get("subscriptions", 0) for s in systems)
    messages_24h = sum(s.get("messages_24h", 0) for s in systems)
    return {"systems": len(systems), "active": len(active), "topics": topics,
            "subscriptions": subscriptions, "messages_24h": messages_24h, "connected": subscriptions > 0}
