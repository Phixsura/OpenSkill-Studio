"""API Webhook Event Catalog — catalog of all available webhook event types."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EventType:
    event_id: str
    name: str  # e.g. "order.created"
    category: str  # "orders", "users", "payments", etc.
    description: str = ""
    schema_fields: list[str] = field(default_factory=list)
    deprecated: bool = False
    version_added: str = "v1"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookEventCatalog:
    def __init__(self) -> None:
        self._events: dict[tuple[str, str], EventType] = {}

    def register(self, installation_id: str, event: EventType) -> EventType:
        if not installation_id: raise ValueError("installation_id is required")
        if not event.name: raise ValueError("Event name is required")
        key = (installation_id, event.event_id)
        if key in self._events: raise ValueError(f"Event {event.event_id} already registered")
        self._events[key] = event
        return event

    def deprecate(self, installation_id: str, event_id: str) -> EventType:
        e = self._get(installation_id, event_id)
        e.deprecated = True
        return e

    def by_category(self, installation_id: str) -> dict[str, list[EventType]]:
        result: dict[str, list[EventType]] = {}
        for (inst, _), e in self._events.items():
            if inst == installation_id:
                result.setdefault(e.category, []).append(e)
        return result

    def search(self, installation_id: str, query: str) -> list[EventType]:
        q = query.lower()
        return [e for (inst, _), e in self._events.items()
                if inst == installation_id and (q in e.name.lower() or q in e.description.lower())]

    def list_events(self, installation_id: str, include_deprecated: bool = False) -> list[EventType]:
        events = [e for (inst, _), e in self._events.items() if inst == installation_id]
        if not include_deprecated: events = [e for e in events if not e.deprecated]
        return events

    def _get(self, installation_id: str, event_id: str) -> EventType:
        e = self._events.get((installation_id, event_id))
        if e is None: raise KeyError(f"Event {event_id} not found")
        return e
