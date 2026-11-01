"""App API Webhook Event Schema Registry — centralized event schema management."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EventSchema:
    event_type: str
    version: str
    fields: list[str]
    required_fields: list[str] = field(default_factory=list)
    deprecated: bool = False

class AppAPIWebhookEventSchemaRegistry:
    def __init__(self) -> None:
        self._schemas: dict[tuple[str, str, str], EventSchema] = {}

    def register(self, installation_id: str, event_type: str, version: str, fields: list[str], required_fields: list[str] | None = None) -> EventSchema:
        if not installation_id: raise ValueError("installation_id is required")
        if not fields: raise ValueError("at least one field required")
        s = EventSchema(event_type=event_type, version=version, fields=fields, required_fields=required_fields or [])
        self._schemas[(installation_id, event_type, version)] = s
        return s

    def deprecate(self, installation_id: str, event_type: str, version: str) -> EventSchema:
        s = self._get(installation_id, event_type, version)
        s.deprecated = True
        return s

    def latest(self, installation_id: str, event_type: str) -> EventSchema | None:
        versions = [(v, s) for (inst, et, v), s in self._schemas.items() if inst == installation_id and et == event_type and not s.deprecated]
        if not versions: return None
        return sorted(versions, key=lambda x: x[0])[-1][1]

    def list_schemas(self, installation_id: str) -> list[EventSchema]:
        return [s for (inst, _, _), s in self._schemas.items() if inst == installation_id]

    def _get(self, installation_id: str, event_type: str, version: str) -> EventSchema:
        s = self._schemas.get((installation_id, event_type, version))
        if s is None: raise KeyError(f"Schema for {event_type} v{version} not found")
        return s
