"""Consumer API Activity Feed — real-time activity stream for consumers."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class ActivityEvent:
    event_id: str
    consumer_id: str
    actor: str
    action: str
    resource_type: str
    resource_id: str
    description: str = ""
    timestamp: datetime | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerActivityFeed:
    def __init__(self, max_per_consumer: int = 1000) -> None:
        self._feeds: dict[tuple[str, str], list[ActivityEvent]] = {}
        self._max = max_per_consumer

    def publish(self, installation_id: str, event: ActivityEvent) -> ActivityEvent:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not event.action:
            raise ValueError("action is required")
        event.timestamp = event.timestamp or datetime.utcnow()
        key = (installation_id, event.consumer_id)
        if key not in self._feeds:
            self._feeds[key] = []
        self._feeds[key].append(event)
        if len(self._feeds[key]) > self._max:
            self._feeds[key] = self._feeds[key][-self._max:]
        return event

    def get_feed(self, installation_id: str, consumer_id: str, resource_type: str | None = None, actor: str | None = None, limit: int = 50) -> list[ActivityEvent]:
        events = self._feeds.get((installation_id, consumer_id), [])
        if resource_type:
            events = [e for e in events if e.resource_type == resource_type]
        if actor:
            events = [e for e in events if e.actor == actor]
        return list(reversed(events[-limit:]))

    def count_by_action(self, installation_id: str, consumer_id: str) -> dict[str, int]:
        events = self._feeds.get((installation_id, consumer_id), [])
        counts: dict[str, int] = {}
        for e in events:
            counts[e.action] = counts.get(e.action, 0) + 1
        return counts

    def get_recent_actors(self, installation_id: str, consumer_id: str, limit: int = 10) -> list[str]:
        events = self._feeds.get((installation_id, consumer_id), [])
        seen: list[str] = []
        for e in reversed(events):
            if e.actor not in seen:
                seen.append(e.actor)
            if len(seen) >= limit:
                break
        return seen
