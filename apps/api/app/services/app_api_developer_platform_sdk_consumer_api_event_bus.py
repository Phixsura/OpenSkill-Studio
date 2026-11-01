"""Consumer Webhook Event Bus — pub/sub event bus with topic filtering."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class Subscription:
    sub_id: str
    consumer_id: str
    topic_pattern: str  # exact or prefix match with *
    webhook_url: str
    active: bool = True
    delivered_count: int = 0


@dataclass
class Event:
    event_id: str
    topic: str
    payload: dict
    published_at: str = ""


@dataclass
class EventBus:
    """Pub/sub event bus with topic-based routing and filtering."""

    _subscriptions: dict[str, Subscription] = field(default_factory=dict)
    _events: list[Event] = field(default_factory=list)
    _max_events: int = 10000

    def subscribe(self, sub: Subscription) -> dict:
        if sub.sub_id in self._subscriptions:
            raise ValueError(f"Subscription {sub.sub_id} already exists")
        if not sub.topic_pattern:
            raise ValueError("Topic pattern is required")
        self._subscriptions[sub.sub_id] = sub
        logger.info("subscribed", sub_id=sub.sub_id, topic=sub.topic_pattern)
        return {"sub_id": sub.sub_id, "topic": sub.topic_pattern}

    def unsubscribe(self, sub_id: str) -> dict:
        if sub_id in self._subscriptions:
            del self._subscriptions[sub_id]
            return {"unsubscribed": True}
        return {"unsubscribed": False}

    def _matches(self, pattern: str, topic: str) -> bool:
        if pattern == "*":
            return True
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return topic == prefix or topic.startswith(prefix + ".")
        return pattern == topic

    def publish(self, event: Event) -> dict:
        if len(self._events) >= self._max_events:
            self._events = self._events[-(self._max_events // 2):]
        self._events.append(event)
        matched_subs = []
        for sub in self._subscriptions.values():
            if sub.active and self._matches(sub.topic_pattern, event.topic):
                sub.delivered_count += 1
                matched_subs.append(sub.sub_id)
        logger.info("event_published", event_id=event.event_id, topic=event.topic,
                     subscribers=len(matched_subs))
        return {"event_id": event.event_id, "topic": event.topic,
                "delivered_to": len(matched_subs), "subscriber_ids": matched_subs}

    def get_subscribers(self, topic: str) -> list[dict]:
        return [
            {"sub_id": s.sub_id, "consumer_id": s.consumer_id,
             "webhook_url": s.webhook_url}
            for s in self._subscriptions.values()
            if s.active and self._matches(s.topic_pattern, topic)
        ]

    def toggle(self, sub_id: str, active: bool) -> dict:
        sub = self._subscriptions.get(sub_id)
        if not sub:
            raise ValueError(f"Subscription {sub_id} not found")
        sub.active = active
        return {"sub_id": sub_id, "active": active}

    def list_subscriptions(self, consumer_id: str | None = None) -> list[dict]:
        subs = list(self._subscriptions.values())
        if consumer_id:
            subs = [s for s in subs if s.consumer_id == consumer_id]
        return [
            {"sub_id": s.sub_id, "topic": s.topic_pattern, "active": s.active,
             "delivered": s.delivered_count, "webhook_url": s.webhook_url}
            for s in subs
        ]

    def get_recent_events(self, topic: str | None = None, limit: int = 20) -> list[dict]:
        events = self._events
        if topic:
            events = [e for e in events if self._matches(topic, e.topic)]
        return [
            {"event_id": e.event_id, "topic": e.topic, "published_at": e.published_at}
            for e in reversed(events[-limit:])
        ]

    def get_stats(self) -> dict:
        subs = list(self._subscriptions.values())
        topics = set()
        for e in self._events:
            topics.add(e.topic)
        return {
            "total_subscriptions": len(subs),
            "active_subscriptions": sum(1 for s in subs if s.active),
            "total_events": len(self._events),
            "unique_topics": len(topics),
            "total_deliveries": sum(s.delivered_count for s in subs),
        }
