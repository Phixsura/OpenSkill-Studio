"""Platform event bus — pub/sub event routing with filtering."""
from __future__ import annotations
from collections import defaultdict


class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list[dict]] = defaultdict(list)
        self._published: int = 0
        self._delivered: int = 0

    def subscribe(self, event_type: str, handler_id: str, filter_fn: callable | None = None) -> dict:
        self._subscribers[event_type].append({"handler": handler_id, "filter": filter_fn})
        return {"event_type": event_type, "handler": handler_id,
                "total_subs": len(self._subscribers[event_type])}

    def publish(self, event_type: str, payload: dict) -> dict:
        self._published += 1
        subs = self._subscribers.get(event_type, [])
        delivered = 0
        for sub in subs:
            if sub["filter"] and not sub["filter"](payload):
                continue
            delivered += 1
        self._delivered += delivered
        return {"event_type": event_type, "delivered": delivered, "total_subs": len(subs)}

    def stats(self) -> dict:
        total_subs = sum(len(s) for s in self._subscribers.values())
        return {"event_types": len(self._subscribers), "total_subscribers": total_subs,
                "published": self._published, "delivered": self._delivered}
