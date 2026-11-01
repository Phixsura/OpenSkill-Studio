"""API Webhook Payload Schema — define and validate webhook payload schemas."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class SchemaField:
    name: str
    field_type: str  # "string", "int", "float", "bool", "object", "array"
    required: bool = True
    description: str = ""

@dataclass
class PayloadSchema:
    schema_id: str
    event_type: str
    version: str
    fields: list[SchemaField] = field(default_factory=list)

@dataclass
class SchemaViolation:
    field: str
    expected: str
    actual: str

VALID_TYPES = {"string": str, "int": int, "float": (int, float), "bool": bool, "object": dict, "array": list}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookPayloadSchema:
    def __init__(self) -> None:
        self._schemas: dict[tuple[str, str, str], PayloadSchema] = {}

    def register(self, installation_id: str, schema: PayloadSchema) -> PayloadSchema:
        if not installation_id: raise ValueError("installation_id is required")
        if not schema.fields: raise ValueError("Schema must have at least one field")
        key = (installation_id, schema.event_type, schema.version)
        self._schemas[key] = schema
        return schema

    def validate(self, installation_id: str, event_type: str, version: str, payload: dict) -> list[SchemaViolation]:
        schema = self._schemas.get((installation_id, event_type, version))
        if schema is None: raise KeyError(f"No schema for {event_type} v{version}")
        violations: list[SchemaViolation] = []
        for f in schema.fields:
            val = payload.get(f.name)
            if val is None:
                if f.required:
                    violations.append(SchemaViolation(f.name, "present", "missing"))
                continue
            expected_type = VALID_TYPES.get(f.field_type)
            if expected_type is None: continue
            # bool-as-int guard
            if f.field_type in ("int", "float") and isinstance(val, bool):
                violations.append(SchemaViolation(f.name, f.field_type, "bool"))
                continue
            if not isinstance(val, expected_type):
                violations.append(SchemaViolation(f.name, f.field_type, type(val).__name__))
        return violations

    def get_schema(self, installation_id: str, event_type: str, version: str) -> PayloadSchema:
        s = self._schemas.get((installation_id, event_type, version))
        if s is None: raise KeyError(f"No schema for {event_type} v{version}")
        return s

    def list_schemas(self, installation_id: str) -> list[PayloadSchema]:
        return [s for (inst, _, _), s in self._schemas.items() if inst == installation_id]

    def versions_for(self, installation_id: str, event_type: str) -> list[str]:
        return [v for (inst, et, v) in self._schemas if inst == installation_id and et == event_type]
