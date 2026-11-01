"""Event Emitter — typed pub/sub within a process with rich semantics.

Node.js EventEmitter-style with enhancements:
- Typed events with listener registration
- Once listeners (auto-remove after first call)
- Wildcard listeners (* matches all events)
- Listener priority ordering
- Max listeners warning (memory leak detection)
- Error event propagation
- Async-style event queue (deferred emit)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Listener:
    callback: callable
    once: bool = False
    priority: int = 0


class EventEmitterService:
    DEFAULT_MAX_LISTENERS = 20

    def __init__(self, max_listeners: int = 0):
        self._listeners: dict[str, list[Listener]] = defaultdict(list)
        self._max = max_listeners or self.DEFAULT_MAX_LISTENERS
        self._emit_count: dict[str, int] = defaultdict(int)
        self._warnings: list[str] = []
        self._queue: list[tuple[str, tuple, dict]] = []

    def on(self, event: str, callback: callable, priority: int = 0) -> callable:
        """Register a listener. Returns the callback for chaining."""
        self._add_listener(event, Listener(callback, once=False, priority=priority))
        return callback

    def once(self, event: str, callback: callable, priority: int = 0) -> callable:
        """Register a one-time listener (removed after first call)."""
        self._add_listener(event, Listener(callback, once=True, priority=priority))
        return callback

    def _add_listener(self, event: str, listener: Listener) -> None:
        listeners = self._listeners[event]
        listeners.append(listener)
        listeners.sort(key=lambda l: l.priority, reverse=True)
        if len(listeners) > self._max:
            self._warnings.append(
                f"MaxListenersExceeded: {event} has {len(listeners)} listeners "
                f"(max {self._max}). Possible memory leak.")

    def off(self, event: str, callback: callable) -> bool:
        """Remove a specific listener."""
        listeners = self._listeners.get(event, [])
        for i, l in enumerate(listeners):
            if l.callback is callback:
                listeners.pop(i)
                return True
        return False

    def remove_all(self, event: str = "") -> int:
        """Remove all listeners for an event (or all events if empty)."""
        if event:
            count = len(self._listeners.pop(event, []))
            return count
        count = sum(len(ls) for ls in self._listeners.values())
        self._listeners.clear()
        return count

    def emit(self, event: str, *args, **kwargs) -> int:
        """Emit an event. Returns number of listeners called."""
        self._emit_count[event] += 1
        count = 0
        to_remove = []

        # Get direct listeners + wildcard listeners
        listeners = list(self._listeners.get(event, []))
        if event != "*":
            listeners.extend(self._listeners.get("*", []))
        listeners.sort(key=lambda l: l.priority, reverse=True)

        for listener in listeners:
            try:
                listener.callback(*args, **kwargs)
                count += 1
            except Exception as e:
                if event != "error":
                    self.emit("error", e, event)
            if listener.once:
                to_remove.append((event, listener))

        # Remove once listeners
        for evt, listener in to_remove:
            ls = self._listeners.get(evt, [])
            if listener in ls:
                ls.remove(listener)
            # Also check wildcard
            ws = self._listeners.get("*", [])
            if listener in ws:
                ws.remove(listener)

        return count

    def emit_deferred(self, event: str, *args, **kwargs) -> None:
        """Queue an event for later processing."""
        self._queue.append((event, args, kwargs))

    def flush_deferred(self) -> int:
        """Process all queued events. Returns count processed."""
        count = 0
        while self._queue:
            event, args, kwargs = self._queue.pop(0)
            self.emit(event, *args, **kwargs)
            count += 1
        return count

    def listener_count(self, event: str) -> int:
        return len(self._listeners.get(event, []))

    def event_names(self) -> list[str]:
        return [e for e, ls in self._listeners.items() if ls]

    def get_emit_count(self, event: str) -> int:
        return self._emit_count.get(event, 0)

    def get_warnings(self) -> list[str]:
        return list(self._warnings)
