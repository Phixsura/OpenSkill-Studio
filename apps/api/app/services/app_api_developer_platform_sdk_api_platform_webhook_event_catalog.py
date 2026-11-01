"""App API Developer Webhook Event Catalog — browsable catalog of all webhook events."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class CatalogEvent:
    event_type: str
    category: str
    description: str
    schema_version: str
    example_payload: str = ""
    subscribers: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformWebhookEventCatalog:
    def __init__(self) -> None:
        self._events: dict[tuple[str, str], CatalogEvent] = {}

    def add(self, installation_id: str, event_type: str, category: str, description: str, schema_version: str, example_payload: str = "") -> CatalogEvent:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, event_type)
        if key in self._events: raise ValueError(f"Event {event_type} exists")
        e = CatalogEvent(event_type=event_type, category=category, description=description, schema_version=schema_version, example_payload=example_payload)
        self._events[key] = e
        return e

    def search(self, installation_id: str, query: str) -> list[CatalogEvent]:
        q = query.lower()
        return [e for (inst, _), e in self._events.items() if inst == installation_id and (q in e.event_type.lower() or q in e.description.lower())]

    def by_category(self, installation_id: str, category: str) -> list[CatalogEvent]:
        return [e for (inst, _), e in self._events.items() if inst == installation_id and e.category == category]

    def categories(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), e in self._events.items():
            if inst == installation_id: counts[e.category] = counts.get(e.category, 0) + 1
        return counts

    def all_events(self, installation_id: str) -> list[CatalogEvent]:
        return sorted([e for (inst, _), e in self._events.items() if inst == installation_id], key=lambda e: e.event_type)
