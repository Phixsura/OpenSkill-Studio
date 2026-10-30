"""API Consumer Webhook Event Type Registry — centralized registry of all event types."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EventTypeEntry:
    event_type: str
    category: str
    description: str = ""
    schema_version: str = "v1"
    deprecated: bool = False
    subscriber_count: int = 0

VALID_CATEGORIES = {"account", "billing", "order", "user", "webhook", "system", "security", "integration"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventTypeRegistry:
    def __init__(self) -> None:
        self._types: dict[tuple[str, str], EventTypeEntry] = {}

    def register(self, installation_id: str, entry: EventTypeEntry) -> EventTypeEntry:
        if not installation_id: raise ValueError("installation_id is required")
        if entry.category not in VALID_CATEGORIES: raise ValueError(f"Invalid category: {entry.category}")
        key = (installation_id, entry.event_type)
        if key in self._types: raise ValueError(f"Event type {entry.event_type} already registered")
        self._types[key] = entry
        return entry

    def deprecate(self, installation_id: str, event_type: str) -> EventTypeEntry:
        key = (installation_id, event_type)
        e = self._types.get(key)
        if e is None: raise KeyError(f"Event type {event_type} not found")
        e.deprecated = True
        return e

    def search(self, installation_id: str, query: str) -> list[EventTypeEntry]:
        q = query.lower()
        return [e for (inst, _), e in self._types.items() if inst == installation_id and (q in e.event_type.lower() or q in e.description.lower())]

    def by_category(self, installation_id: str, category: str) -> list[EventTypeEntry]:
        return [e for (inst, _), e in self._types.items() if inst == installation_id and e.category == category]

    def active_types(self, installation_id: str) -> list[EventTypeEntry]:
        return [e for (inst, _), e in self._types.items() if inst == installation_id and not e.deprecated]

    def list_types(self, installation_id: str) -> list[EventTypeEntry]:
        return [e for (inst, _), e in self._types.items() if inst == installation_id]
