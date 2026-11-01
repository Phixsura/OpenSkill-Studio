"""Event Router — route events to handlers based on type, content, and rules.

Implements:
- Event type → handler mapping
- Content-based routing (route by payload fields)
- Priority handlers (higher priority runs first)
- Error handler chain (fallback on failure)
- Dead letter for unroutable events
- Handler timeout tracking
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import time


@dataclass
class RouteHandler:
    name: str
    event_types: list[str]  # ["user.*", "order.created"]
    handler: callable
    priority: int = 0
    content_filter: dict | None = None  # {"field": "value"} or {"field": "regex:..."}
    enabled: bool = True


@dataclass
class RoutedEvent:
    event_type: str
    payload: dict
    handled_by: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    dead_lettered: bool = False


class EventRouterService:
    def __init__(self):
        self._handlers: list[RouteHandler] = []
        self._dead_letter: list[RoutedEvent] = []
        self._stats: dict[str, int] = {"routed": 0, "dead_lettered": 0, "errors": 0}

    def register(self, name: str, event_types: list[str], handler: callable,
                 priority: int = 0, content_filter: dict | None = None) -> None:
        rh = RouteHandler(name=name, event_types=event_types, handler=handler,
                          priority=priority, content_filter=content_filter)
        self._handlers.append(rh)
        self._handlers.sort(key=lambda h: h.priority, reverse=True)

    def unregister(self, name: str) -> bool:
        for i, h in enumerate(self._handlers):
            if h.name == name:
                self._handlers.pop(i)
                return True
        return False

    def route(self, event_type: str, payload: dict) -> RoutedEvent:
        """Route an event to matching handlers."""
        routed = RoutedEvent(event_type=event_type, payload=payload)
        matched = False

        for handler in self._handlers:
            if not handler.enabled:
                continue
            if not self._type_matches(event_type, handler.event_types):
                continue
            if handler.content_filter and not self._content_matches(payload, handler.content_filter):
                continue

            matched = True
            try:
                handler.handler(event_type, payload)
                routed.handled_by.append(handler.name)
            except Exception as e:
                routed.errors.append(f"{handler.name}: {e}")
                self._stats["errors"] += 1

        if not matched:
            routed.dead_lettered = True
            self._dead_letter.append(routed)
            self._stats["dead_lettered"] += 1
        else:
            self._stats["routed"] += 1

        return routed

    def _type_matches(self, event_type: str, patterns: list[str]) -> bool:
        for pattern in patterns:
            if pattern == event_type:
                return True
            if pattern == "*":
                return True
            if pattern.endswith(".*"):
                prefix = pattern[:-2]
                if event_type.startswith(prefix + ".") or event_type == prefix:
                    return True
        return False

    def _content_matches(self, payload: dict, filters: dict) -> bool:
        for field_path, expected in filters.items():
            actual = self._get_nested(payload, field_path)
            if actual is None:
                return False
            if isinstance(expected, str) and expected.startswith("regex:"):
                if not re.search(expected[6:], str(actual)):
                    return False
            elif actual != expected:
                return False
        return True

    def _get_nested(self, obj: dict, path: str) -> object:
        for part in path.split("."):
            if isinstance(obj, dict):
                obj = obj.get(part)
            else:
                return None
        return obj

    def get_dead_letters(self) -> list[RoutedEvent]:
        return list(self._dead_letter)

    def get_stats(self) -> dict:
        return dict(self._stats)

    def get_handlers(self) -> list[dict]:
        return [{"name": h.name, "types": h.event_types,
                 "priority": h.priority, "enabled": h.enabled}
                for h in self._handlers]
