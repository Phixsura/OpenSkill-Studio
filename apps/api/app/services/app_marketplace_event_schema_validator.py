"""Event Schema Validator — validate webhook event payloads against schemas.

Ensures events conform to their registered schemas before dispatch,
with detailed error reporting and schema evolution support.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class FieldSchema:
    name: str
    field_type: str  # string, int, float, bool, list, dict, enum
    required: bool = True
    enum_values: list[str] = field(default_factory=list)
    min_length: int | None = None
    max_length: int | None = None
    nested: dict | None = None  # for dict type: {field: FieldSchema}


@dataclass
class EventSchema:
    event_type: str
    version: int
    fields: list[FieldSchema]
    description: str = ""


class EventSchemaValidator:
    """Validates event payloads against registered schemas."""

    TYPE_MAP = {"string": str, "int": int, "float": (int, float),
                "bool": bool, "list": list, "dict": dict}

    def __init__(self):
        self._schemas: dict[str, EventSchema] = {}

    def register(self, schema: EventSchema) -> None:
        self._schemas[f"{schema.event_type}:v{schema.version}"] = schema

    def get_schema(self, event_type: str, version: int = 1) -> EventSchema | None:
        return self._schemas.get(f"{event_type}:v{version}")

    def validate(self, event_type: str, payload: dict, version: int = 1) -> tuple[bool, list[str]]:
        """Validate payload against schema. Returns (valid, errors)."""
        schema = self.get_schema(event_type, version)
        if not schema:
            return True, []  # no schema = pass through

        errors = []
        for field_def in schema.fields:
            value = payload.get(field_def.name)

            # Required check
            if field_def.required and (value is None or value == ""):
                errors.append(f"Missing required field: {field_def.name}")
                continue

            if value is None:
                continue

            # Type check
            if field_def.field_type == "enum":
                if value not in field_def.enum_values:
                    errors.append(f"Field '{field_def.name}': must be one of {field_def.enum_values}, got '{value}'")
            else:
                expected = self.TYPE_MAP.get(field_def.field_type)
                if expected and not isinstance(value, expected):
                    errors.append(f"Field '{field_def.name}': expected {field_def.field_type}, got {type(value).__name__}")

            # Length check
            if isinstance(value, (str, list)):
                if field_def.min_length is not None and len(value) < field_def.min_length:
                    errors.append(f"Field '{field_def.name}': length {len(value)} < min {field_def.min_length}")
                if field_def.max_length is not None and len(value) > field_def.max_length:
                    errors.append(f"Field '{field_def.name}': length {len(value)} > max {field_def.max_length}")

        # Unknown fields warning (not error)
        known = {f.name for f in schema.fields}
        unknown = set(payload.keys()) - known
        for u in sorted(unknown):
            errors.append(f"Unknown field: {u} (not in schema)")

        # Only required/type/length are hard errors
        hard_errors = [e for e in errors if "Unknown" not in e]
        return len(hard_errors) == 0, errors

    def list_schemas(self) -> list[dict]:
        return [{"event_type": s.event_type, "version": s.version,
                 "fields": len(s.fields), "description": s.description}
                for s in self._schemas.values()]
