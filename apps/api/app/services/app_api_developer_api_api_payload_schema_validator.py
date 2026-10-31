"""App API Developer API Payload Schema Validator — validate request/response schemas."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)

VALIDATORS = {
    "string": lambda v: isinstance(v, str),
    "int": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "float": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "bool": lambda v: isinstance(v, bool),
    "email": lambda v: isinstance(v, str) and bool(_EMAIL_RE.match(v)),
    "uuid": lambda v: isinstance(v, str) and bool(_UUID_RE.match(v)),
    "list": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
}

@dataclass
class SchemaField:
    name: str
    field_type: str
    required: bool = True

@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)

class AppAPIDeveloperAPIApiPayloadSchemaValidator:
    def __init__(self) -> None:
        self._schemas: dict[tuple[str, str], list[SchemaField]] = {}

    def register(self, installation_id: str, schema_id: str, fields: list[dict]) -> list[SchemaField]:
        if not installation_id: raise ValueError("installation_id is required")
        parsed = []
        for f in fields:
            if f["type"] not in VALIDATORS: raise ValueError(f"Unknown type: {f['type']}")
            parsed.append(SchemaField(name=f["name"], field_type=f["type"], required=f.get("required", True)))
        self._schemas[(installation_id, schema_id)] = parsed
        return parsed

    def validate(self, installation_id: str, schema_id: str, payload: dict) -> ValidationResult:
        key = (installation_id, schema_id)
        schema = self._schemas.get(key)
        if schema is None: raise KeyError(f"Schema {schema_id} not found")
        errors: list[str] = []
        for f in schema:
            if f.name not in payload:
                if f.required: errors.append(f"Missing required field: {f.name}")
                continue
            val = payload[f.name]
            validator = VALIDATORS.get(f.field_type)
            if validator and not validator(val):
                errors.append(f"Field {f.name}: expected {f.field_type}, got {type(val).__name__}")
        return ValidationResult(valid=len(errors) == 0, errors=errors)
