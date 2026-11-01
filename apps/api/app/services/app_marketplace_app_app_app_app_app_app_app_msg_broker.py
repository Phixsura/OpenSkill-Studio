"""Message broker topic manager — publish/subscribe message routing."""
from __future__ import annotations
from collections import defaultdict


class MessageBroker:
    def __init__(self):
        self._topics: dict[str, list[str]] = {}
        self._messages: dict[str, list[dict]] = defaultdict(list)
        self._delivered: int = 0

    def create_topic(self, name: str) -> dict:
        self._topics[name] = []
        return {"topic": name, "created": True}

    def subscribe(self, topic: str, subscriber: str) -> dict:
        if topic not in self._topics:
            self._topics[topic] = []
        if subscriber not in self._topics[topic]:
            self._topics[topic].append(subscriber)
        return {"topic": topic, "subscriber": subscriber,
                "total_subscribers": len(self._topics[topic])}

    def publish(self, topic: str, message: dict) -> dict:
        subs = self._topics.get(topic, [])
        for sub in subs:
            self._messages[sub].append({"topic": topic, **message})
            self._delivered += 1
        return {"topic": topic, "delivered_to": len(subs), "subscribers": subs}

    def consume(self, subscriber: str, limit: int = 10) -> list[dict]:
        msgs = self._messages.get(subscriber, [])[:limit]
        self._messages[subscriber] = self._messages.get(subscriber, [])[limit:]
        return msgs

    def stats(self) -> dict:
        return {"topics": len(self._topics), "total_delivered": self._delivered,
                "pending": sum(len(v) for v in self._messages.values())}
