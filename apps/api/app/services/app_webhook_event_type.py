"""App Webhook Event Type — manage webhook event type registry.

Manages event types:
- Register event types with schemas
- Categorize events
- Track event emission counts
- Per-installation scoped types
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class EventType:
    """A webhook event type definition."""

    event_type: str  # e.g., "app.installed", "webhook.delivered"
    description: str
    category: str = "general"
    schema_fields: list[str] = field(default_factory=list)
    emit_count: int = 0


class AppWebhookEventType:
    """Manage webhook event type registry."""

    def __init__(self) -> None:
        self._types: dict[tuple[str, str], EventType] = {}

    def register(
        self, installation_id: str, event_type: str, description: str,
        category: str = "general", schema_fields: list[str] | None = None,
    ) -> EventType:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not event_type:
            raise ValueError("event_type is required")

        et = EventType(
            event_type=event_type, description=description,
            category=category, schema_fields=schema_fields or [],
        )
        self._types[(installation_id, event_type)] = et
        return et

    def record_emit(self, installation_id: str, event_type: str) -> EventType:
        et = self._get(installation_id, event_type)
        et.emit_count += 1
        return et

    def list_types(self, installation_id: str, category: str | None = None) -> list[EventType]:
        types = [t for (inst, _), t in self._types.items() if inst == installation_id]
        if category:
            types = [t for t in types if t.category == category]
        return sorted(types, key=lambda t: t.event_type)

    def categories(self, installation_id: str) -> list[str]:
        cats: set[str] = set()
        for (inst, _), t in self._types.items():
            if inst == installation_id:
                cats.add(t.category)
        return sorted(cats)

    def _get(self, installation_id: str, event_type: str) -> EventType:
        key = (installation_id, event_type)
        t = self._types.get(key)
        if t is None:
            raise KeyError(f"Event type {event_type} not found")
        return t
