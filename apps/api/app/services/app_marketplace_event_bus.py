"""Event Bus — pub/sub event system for extension communication.

Provides a lightweight in-process event bus that extensions and
platform services use to communicate asynchronously.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable


@dataclass
class Event:
    event_type: str
    payload: dict
    source: str
    timestamp: str = ""
    event_id: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if not self.event_id:
            self.event_id = f"evt-{id(self)}"


EventHandler = Callable[[Event], None]


class EventBus:
    """Pub/sub event bus for decoupled extension communication."""

    def __init__(self):
        self._handlers: dict[str, list[tuple[str, EventHandler]]] = defaultdict(list)
        self._event_log: list[Event] = []
        self._dead_letter: list[Event] = []

    def subscribe(self, event_type: str, handler: EventHandler, subscriber_id: str = "") -> None:
        """Subscribe to an event type."""
        self._handlers[event_type].append((subscriber_id, handler))

    def unsubscribe(self, event_type: str, subscriber_id: str) -> bool:
        """Unsubscribe by subscriber ID."""
        before = len(self._handlers[event_type])
        self._handlers[event_type] = [
            (sid, h) for sid, h in self._handlers[event_type] if sid != subscriber_id
        ]
        return len(self._handlers[event_type]) < before

    def publish(self, event: Event) -> int:
        """Publish an event. Returns number of handlers invoked."""
        self._event_log.append(event)
        handlers = self._handlers.get(event.event_type, [])
        if not handlers:
            self._dead_letter.append(event)
            return 0
        invoked = 0
        for _, handler in handlers:
            try:
                handler(event)
                invoked += 1
            except Exception:
                pass  # handler failures are isolated
        return invoked

    def emit(self, event_type: str, payload: dict, source: str = "system") -> int:
        """Convenience: create and publish an event in one call."""
        return self.publish(Event(event_type=event_type, payload=payload, source=source))

    def subscriber_count(self, event_type: str) -> int:
        return len(self._handlers.get(event_type, []))

    def get_event_log(self, event_type: str | None = None, limit: int = 100) -> list[Event]:
        log = self._event_log
        if event_type:
            log = [e for e in log if e.event_type == event_type]
        return log[-limit:]

    def get_dead_letters(self) -> list[Event]:
        return list(self._dead_letter)

    def clear(self) -> None:
        self._handlers.clear()
        self._event_log.clear()
        self._dead_letter.clear()
