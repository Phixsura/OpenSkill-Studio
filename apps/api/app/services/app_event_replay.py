"""App Event Replay — replay stored events for debugging.

Manages event replay:
- Store events with metadata
- Replay events by time range or type
- Filter events by source
- Per-installation scoped events
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class StoredEvent:
    """A stored event for replay."""

    event_id: str
    event_type: str
    source: str
    payload: dict
    timestamp: float = field(default_factory=time.time)
    replayed: bool = False


class AppEventReplay:
    """Store and replay events for debugging."""

    def __init__(self, max_events: int = 10000) -> None:
        self._max = max(1, max_events)
        self._events: dict[str, list[StoredEvent]] = {}

    def store(
        self, installation_id: str, event_id: str,
        event_type: str, source: str, payload: dict,
    ) -> StoredEvent:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not event_type:
            raise ValueError("event_type is required")

        event = StoredEvent(
            event_id=event_id, event_type=event_type,
            source=source, payload=payload,
        )
        events = self._events.setdefault(installation_id, [])
        events.append(event)
        if len(events) > self._max:
            self._events[installation_id] = events[-self._max:]
        return event

    def replay(
        self, installation_id: str, event_type: str | None = None,
        source: str | None = None, since: float | None = None,
        limit: int = 100,
    ) -> list[StoredEvent]:
        events = list(self._events.get(installation_id, []))
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if source:
            events = [e for e in events if e.source == source]
        if since is not None:
            events = [e for e in events if e.timestamp >= since]

        result = events[-limit:]
        for e in result:
            e.replayed = True
        return result

    def get_event(self, installation_id: str, event_id: str) -> StoredEvent:
        for e in self._events.get(installation_id, []):
            if e.event_id == event_id:
                return e
        raise KeyError(f"Event {event_id} not found")

    def event_types(self, installation_id: str) -> list[str]:
        types: set[str] = set()
        for e in self._events.get(installation_id, []):
            types.add(e.event_type)
        return sorted(types)

    def count(self, installation_id: str, event_type: str | None = None) -> int:
        events = self._events.get(installation_id, [])
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return len(events)
