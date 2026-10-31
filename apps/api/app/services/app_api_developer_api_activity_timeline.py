"""App API Developer Activity Timeline — chronological platform activity feed."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ActivityEvent:
    event_id: str
    actor: str
    action: str
    resource: str
    timestamp: float = field(default_factory=time.time)

class AppAPIDeveloperAPIActivityTimeline:
    def __init__(self, max_events: int = 5000) -> None:
        self._max = max(1, max_events)
        self._events: dict[str, list[ActivityEvent]] = {}

    def record(self, installation_id: str, event_id: str, actor: str, action: str, resource: str) -> ActivityEvent:
        if not installation_id: raise ValueError("installation_id is required")
        e = ActivityEvent(event_id=event_id, actor=actor, action=action, resource=resource)
        events = self._events.setdefault(installation_id, [])
        events.append(e)
        if len(events) > self._max: self._events[installation_id] = events[-self._max:]
        return e

    def recent(self, installation_id: str, limit: int = 20) -> list[ActivityEvent]:
        return list(reversed(self._events.get(installation_id, [])[-limit:]))

    def by_actor(self, installation_id: str, actor: str) -> list[ActivityEvent]:
        return [e for e in self._events.get(installation_id, []) if e.actor == actor]

    def count(self, installation_id: str) -> int:
        return len(self._events.get(installation_id, []))
