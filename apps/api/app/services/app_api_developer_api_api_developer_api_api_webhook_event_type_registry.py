"""App API Developer Webhook Event Type Registry — define and manage event types."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EventType:
    event_type: str
    description: str
    schema_version: str
    category: str  # "resource", "lifecycle", "notification", "system"
    deprecated: bool = False
    subscriber_count: int = 0

class AppAPIDeveloperAPIApiDeveloperApiApiWebhookEventTypeRegistry:
    def __init__(self) -> None:
        self._types: dict[tuple[str, str], EventType] = {}

    def register(self, installation_id: str, event_type: str, description: str, schema_version: str, category: str) -> EventType:
        if not installation_id: raise ValueError("installation_id is required")
        if category not in ("resource", "lifecycle", "notification", "system"): raise ValueError("invalid category")
        key = (installation_id, event_type)
        if key in self._types: raise ValueError(f"Event type {event_type} exists")
        t = EventType(event_type=event_type, description=description, schema_version=schema_version, category=category)
        self._types[key] = t
        return t

    def deprecate(self, installation_id: str, event_type: str) -> EventType:
        key = (installation_id, event_type)
        t = self._types.get(key)
        if t is None: raise KeyError(f"Event type {event_type} not found")
        t.deprecated = True
        return t

    def by_category(self, installation_id: str, category: str) -> list[EventType]:
        return [t for (inst, _), t in self._types.items() if inst == installation_id and t.category == category]

    def active_types(self, installation_id: str) -> list[EventType]:
        return [t for (inst, _), t in self._types.items() if inst == installation_id and not t.deprecated]

    def all_types(self, installation_id: str) -> list[EventType]:
        return [t for (inst, _), t in self._types.items() if inst == installation_id]

    def category_counts(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), t in self._types.items():
            if inst == installation_id: counts[t.category] = counts.get(t.category, 0) + 1
        return counts
