"""App API Developer Webhook Event Schema Registry — versioned event schemas."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EventSchema:
    event_type: str
    version: str
    fields: dict[str, str]  # field_name -> type
    required_fields: list[str] = field(default_factory=list)
    description: str = ""

class AppAPIDeveloperAPIWebhookEventSchemaRegistry:
    def __init__(self) -> None:
        self._schemas: dict[tuple[str, str, str], EventSchema] = {}  # (inst, event, version)

    def register(self, installation_id: str, event_type: str, version: str, fields: dict[str, str], required_fields: list[str] | None = None, description: str = "") -> EventSchema:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, event_type, version)
        if key in self._schemas: raise ValueError(f"Schema {event_type}@{version} exists")
        s = EventSchema(event_type=event_type, version=version, fields=fields, required_fields=required_fields or [], description=description)
        self._schemas[key] = s
        return s

    def get(self, installation_id: str, event_type: str, version: str) -> EventSchema:
        key = (installation_id, event_type, version)
        s = self._schemas.get(key)
        if s is None: raise KeyError(f"Schema {event_type}@{version} not found")
        return s

    def latest(self, installation_id: str, event_type: str) -> EventSchema | None:
        versions = [(v, s) for (inst, et, v), s in self._schemas.items() if inst == installation_id and et == event_type]
        if not versions: return None
        return max(versions, key=lambda x: x[0])[1]

    def list_events(self, installation_id: str) -> list[str]:
        return sorted(set(et for (inst, et, _) in self._schemas if inst == installation_id))

    def validate_payload(self, installation_id: str, event_type: str, version: str, payload: dict) -> list[str]:
        s = self.get(installation_id, event_type, version)
        errors: list[str] = []
        for rf in s.required_fields:
            if rf not in payload: errors.append(f"Missing required field: {rf}")
        return errors
