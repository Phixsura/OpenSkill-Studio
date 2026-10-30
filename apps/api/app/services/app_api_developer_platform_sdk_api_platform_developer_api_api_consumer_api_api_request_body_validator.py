"""API Consumer Request Body Validator — validate JSON request bodies against schemas."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import structlog

log = structlog.get_logger()

@dataclass
class BodySchema:
    endpoint: str
    method: str
    required_fields: list[str] = field(default_factory=list)
    field_types: dict[str, str] = field(default_factory=dict)  # field → "string"|"int"|"bool"|"array"|"object"
    max_body_bytes: int = 1048576

@dataclass
class BodyValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)

TYPE_MAP = {"string": str, "int": int, "float": (int, float), "bool": bool, "array": list, "object": dict}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestBodyValidator:
    def __init__(self) -> None:
        self._schemas: dict[tuple[str, str, str], BodySchema] = {}
        self._stats: dict[str, dict[str, int]] = {}

    def register_schema(self, installation_id: str, schema: BodySchema) -> BodySchema:
        if not installation_id: raise ValueError("installation_id is required")
        self._schemas[(installation_id, schema.method.upper(), schema.endpoint)] = schema
        return schema

    def validate(self, installation_id: str, method: str, endpoint: str, body: str) -> BodyValidationResult:
        schema = self._schemas.get((installation_id, method.upper(), endpoint))
        if schema is None: return BodyValidationResult(valid=True)
        errors: list[str] = []
        if len(body.encode("utf-8")) > schema.max_body_bytes:
            errors.append(f"Body too large: max {schema.max_body_bytes} bytes")
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            errors.append("Invalid JSON body")
            return BodyValidationResult(valid=False, errors=errors)
        for rf in schema.required_fields:
            if rf not in data: errors.append(f"Missing required field: {rf}")
        for fname, ftype in schema.field_types.items():
            if fname not in data: continue
            val = data[fname]
            if ftype in ("int", "float") and isinstance(val, bool):
                errors.append(f"Field {fname}: expected {ftype}, got bool")
            elif ftype in TYPE_MAP and not isinstance(val, TYPE_MAP[ftype]):
                errors.append(f"Field {fname}: expected {ftype}")
        stats = self._stats.setdefault(installation_id, {"valid": 0, "invalid": 0})
        stats["valid" if not errors else "invalid"] += 1
        return BodyValidationResult(valid=len(errors) == 0, errors=errors)

    def validation_rate(self, installation_id: str) -> float:
        s = self._stats.get(installation_id, {"valid": 0, "invalid": 0})
        total = s["valid"] + s["invalid"]
        return round((s["valid"] / total) * 100, 1) if total > 0 else 0.0

    def list_schemas(self, installation_id: str) -> list[BodySchema]:
        return [s for (inst, _, _), s in self._schemas.items() if inst == installation_id]
