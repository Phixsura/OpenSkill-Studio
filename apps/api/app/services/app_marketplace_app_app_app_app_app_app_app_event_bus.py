"""Event bus — publish-subscribe event system with topic routing."""
from __future__ import annotations


class EventBus:
    def __init__(self):
        self._subscriptions: dict[str, list[dict]] = {}
        self._published = 0
        self._delivered = 0

    def subscribe(self, topic: str, *, subscriber: str, filter_fn: str = "") -> dict:
        self._subscriptions.setdefault(topic, []).append(
            {"subscriber": subscriber, "filter": filter_fn})
        return {"topic": topic, "subscriber": subscriber,
                "total_subscribers": len(self._subscriptions[topic])}

    def unsubscribe(self, topic: str, *, subscriber: str) -> dict:
        subs = self._subscriptions.get(topic, [])
        before = len(subs)
        self._subscriptions[topic] = [s for s in subs if s["subscriber"] != subscriber]
        return {"removed": before > len(self._subscriptions[topic])}

    def publish(self, topic: str, *, payload: dict) -> dict:
        self._published += 1
        subs = self._subscriptions.get(topic, [])
        delivered = len(subs)
        self._delivered += delivered
        return {"topic": topic, "delivered_to": delivered,
                "subscribers": [s["subscriber"] for s in subs]}

    def topics(self) -> list[dict]:
        return [{"topic": t, "subscribers": len(s)}
                for t, s in sorted(self._subscriptions.items())]

    def stats(self) -> dict:
        total_subs = sum(len(s) for s in self._subscriptions.values())
        return {"topics": len(self._subscriptions), "total_subscribers": total_subs,
                "published": self._published, "delivered": self._delivered}
