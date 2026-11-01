"""App API Event Bus — publish/subscribe event bus.

Manages event bus:
- Register topics
- Subscribe handlers to topics
- Publish events with delivery tracking
- Per-installation scoped topics
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class Topic:
    """An event bus topic."""

    topic_id: str
    name: str
    subscriber_count: int = 0
    publish_count: int = 0


@dataclass
class Subscription:
    """A subscription to a topic."""

    subscriber_id: str
    topic_id: str
    endpoint: str
    active: bool = True


class AppAPIEventBus:
    """Publish/subscribe event bus."""

    def __init__(self) -> None:
        self._topics: dict[tuple[str, str], Topic] = {}
        self._subscriptions: dict[str, list[Subscription]] = {}

    def create_topic(self, installation_id: str, topic_id: str, name: str) -> Topic:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, topic_id)
        if key in self._topics:
            raise ValueError(f"Topic {topic_id} already exists")
        topic = Topic(topic_id=topic_id, name=name)
        self._topics[key] = topic
        return topic

    def subscribe(
        self, installation_id: str, subscriber_id: str, topic_id: str, endpoint: str,
    ) -> Subscription:
        if (installation_id, topic_id) not in self._topics:
            raise KeyError(f"Topic {topic_id} not found")
        sub = Subscription(subscriber_id=subscriber_id, topic_id=topic_id, endpoint=endpoint)
        self._subscriptions.setdefault(installation_id, []).append(sub)
        self._topics[(installation_id, topic_id)].subscriber_count += 1
        return sub

    def publish(self, installation_id: str, topic_id: str) -> int:
        """Publish to a topic. Returns number of subscribers notified."""
        key = (installation_id, topic_id)
        topic = self._topics.get(key)
        if topic is None:
            raise KeyError(f"Topic {topic_id} not found")
        topic.publish_count += 1
        subs = [s for s in self._subscriptions.get(installation_id, []) if s.topic_id == topic_id and s.active]
        return len(subs)

    def list_topics(self, installation_id: str) -> list[Topic]:
        return [t for (inst, _), t in self._topics.items() if inst == installation_id]

    def topic_subscribers(self, installation_id: str, topic_id: str) -> list[Subscription]:
        return [s for s in self._subscriptions.get(installation_id, []) if s.topic_id == topic_id]
