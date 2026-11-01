"""API Consumer Webhook Event Schema Registry — register and validate event schemas."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EventSchema:
    event_type: str
    version: str
    fields: dict[str, str] = field(default_factory=dict)  # field → type
    required_fields: list[str] = field(default_factory=list)
    description: str = ""

@dataclass
class SchemaValidation:
    valid: bool
    errors: list[str] = field(default_factory=list)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventSchemaRegistry:
    def __init__(self) -> None:
        self._schemas: dict[tuple[str, str, str], EventSchema] = {}

    def register(self, installation_id: str, schema: EventSchema) -> EventSchema:
        if not installation_id: raise ValueError("installation_id is required")
        if not schema.event_type: raise ValueError("event_type is required")
        self._schemas[(installation_id, schema.event_type, schema.version)] = schema
        return schema

    def validate_event(self, installation_id: str, event_type: str, version: str, payload: dict) -> SchemaValidation:
        schema = self._schemas.get((installation_id, event_type, version))
        if schema is None: return SchemaValidation(valid=True)  # no schema = pass through
        errors: list[str] = []
        for rf in schema.required_fields:
            if rf not in payload: errors.append(f"Missing: {rf}")
        TYPE_MAP = {"string": str, "int": int, "float": (int, float), "bool": bool, "list": list, "object": dict}
        for fname, ftype in schema.fields.items():
            if fname not in payload: continue
            val = payload[fname]
            if ftype in ("int", "float") and isinstance(val, bool):
                errors.append(f"{fname}: expected {ftype}, got bool")
            elif ftype in TYPE_MAP and not isinstance(val, TYPE_MAP[ftype]):
                errors.append(f"{fname}: expected {ftype}")
        return SchemaValidation(valid=len(errors) == 0, errors=errors)

    def list_schemas(self, installation_id: str) -> list[EventSchema]:
        return [s for (inst, _, _), s in self._schemas.items() if inst == installation_id]

    def versions_for(self, installation_id: str, event_type: str) -> list[str]:
        return [v for (inst, et, v) in self._schemas if inst == installation_id and et == event_type]
