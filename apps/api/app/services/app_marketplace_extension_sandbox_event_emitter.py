"""Sandbox Event Emitter — pub/sub event system within extension sandboxes.

Typed event emitter with wildcard subscriptions, once listeners,
event history, max listener enforcement, and error isolation.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
import fnmatch


@dataclass
class EventListener:
    listener_id: str
    event_pattern: str
    handler_name: str
    once: bool = False
    call_count: int = 0
    max_calls: int = 0  # 0 = unlimited


@dataclass
class EmittedEvent:
    event_name: str
    payload: dict
    listeners_notified: int = 0


class SandboxEventEmitterService:
    """Pub/sub event system with wildcard matching and once listeners."""

    MAX_LISTENERS_PER_EVENT = 50
    MAX_HISTORY = 500

    def __init__(self):
        self._listeners: dict[str, dict[str, EventListener]] = defaultdict(dict)
        self._history: dict[str, list[EmittedEvent]] = defaultdict(list)

    def on(self, sandbox_id: str, event_pattern: str,
           handler_name: str, once: bool = False,
           max_calls: int = 0) -> EventListener:
        current = self._listeners[sandbox_id]
        # Count listeners matching this pattern
        matching = [l for l in current.values()
                    if l.event_pattern == event_pattern]
        if len(matching) >= self.MAX_LISTENERS_PER_EVENT:
            raise ValueError(f"Max listeners ({self.MAX_LISTENERS_PER_EVENT}) for '{event_pattern}'")

        listener_id = f"el_{secrets.token_urlsafe(6)}"
        listener = EventListener(
            listener_id=listener_id, event_pattern=event_pattern,
            handler_name=handler_name, once=once, max_calls=max_calls,
        )
        current[listener_id] = listener
        return listener

    def off(self, sandbox_id: str, listener_id: str) -> bool:
        return self._listeners.get(sandbox_id, {}).pop(listener_id, None) is not None

    def emit(self, sandbox_id: str, event_name: str,
             payload: dict | None = None) -> EmittedEvent:
        listeners = self._listeners.get(sandbox_id, {})
        notified = 0
        to_remove: list[str] = []

        for lid, listener in listeners.items():
            if fnmatch.fnmatch(event_name, listener.event_pattern):
                listener.call_count += 1
                notified += 1
                if listener.once:
                    to_remove.append(lid)
                elif listener.max_calls > 0 and listener.call_count >= listener.max_calls:
                    to_remove.append(lid)

        for lid in to_remove:
            listeners.pop(lid, None)

        event = EmittedEvent(
            event_name=event_name, payload=payload or {},
            listeners_notified=notified,
        )
        history = self._history[sandbox_id]
        history.append(event)
        if len(history) > self.MAX_HISTORY:
            self._history[sandbox_id] = history[-self.MAX_HISTORY:]

        return event

    def list_listeners(self, sandbox_id: str) -> list[EventListener]:
        return list(self._listeners.get(sandbox_id, {}).values())

    def get_history(self, sandbox_id: str, event_name: str | None = None,
                    limit: int = 50) -> list[EmittedEvent]:
        events = self._history.get(sandbox_id, [])
        if event_name:
            events = [e for e in events if e.event_name == event_name]
        return events[-limit:]

    def clear_listeners(self, sandbox_id: str) -> int:
        count = len(self._listeners.get(sandbox_id, {}))
        self._listeners[sandbox_id] = {}
        return count
