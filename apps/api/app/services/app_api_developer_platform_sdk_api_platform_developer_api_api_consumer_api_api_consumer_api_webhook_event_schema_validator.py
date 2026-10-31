"""Webhook Event Schema Validator — validate webhook payloads against registered schemas."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class SchemaField:
    name: str
    field_type: str  # "string", "integer", "boolean", "array", "object"
    required: bool = True
    min_length: int | None = None
    max_length: int | None = None

@dataclass
class EventSchema:
    schema_id: str
    event_type: str
    version: str
    fields: list[SchemaField] = field(default_factory=list)

@dataclass
class ValidationError:
    field: str
    message: str

@dataclass
class ValidationResult:
    valid: bool
    errors: list[ValidationError] = field(default_factory=list)

TYPE_CHECKS = {
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventSchemaValidator:
    def __init__(self) -> None:
        self._schemas: dict[tuple[str, str], EventSchema] = {}

    def register(self, installation_id: str, schema: EventSchema) -> EventSchema:
        if not installation_id:
            raise ValueError("installation_id is required")
        self._schemas[(installation_id, schema.schema_id)] = schema
        log.info("schema_registered", installation_id=installation_id, schema_id=schema.schema_id, event_type=schema.event_type)
        return schema

    def get_schema(self, installation_id: str, schema_id: str) -> EventSchema | None:
        return self._schemas.get((installation_id, schema_id))

    def validate(self, installation_id: str, schema_id: str, payload: dict) -> ValidationResult:
        schema = self._schemas.get((installation_id, schema_id))
        if not schema:
            return ValidationResult(valid=False, errors=[ValidationError(field="", message="Schema not found")])
        errors: list[ValidationError] = []
        for f in schema.fields:
            val = payload.get(f.name)
            if val is None:
                if f.required:
                    errors.append(ValidationError(field=f.name, message="required field missing"))
                continue
            checker = TYPE_CHECKS.get(f.field_type)
            if checker and not checker(val):
                errors.append(ValidationError(field=f.name, message=f"expected {f.field_type}"))
                continue
            if f.field_type == "string":
                if f.min_length is not None and len(val) < f.min_length:
                    errors.append(ValidationError(field=f.name, message=f"min length {f.min_length}"))
                if f.max_length is not None and len(val) > f.max_length:
                    errors.append(ValidationError(field=f.name, message=f"max length {f.max_length}"))
        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def list_schemas(self, installation_id: str) -> list[EventSchema]:
        return [s for (inst, _), s in self._schemas.items() if inst == installation_id]
