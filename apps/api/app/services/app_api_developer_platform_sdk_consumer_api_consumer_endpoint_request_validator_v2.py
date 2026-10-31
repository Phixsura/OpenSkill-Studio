"""Consumer API Endpoint Request Validator V2 — advanced request validation with nested fields."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class ValidationRule:
    field_path: str  # supports dot notation: "data.user.email"
    rule_type: str  # "required", "type", "min_length", "max_length", "pattern", "range"
    value: str = ""
    message: str = ""

@dataclass
class ValidationSchema:
    schema_id: str
    endpoint_path: str
    method: str
    rules: list[ValidationRule] = field(default_factory=list)

@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)

def _get_nested(obj: dict, path: str) -> object:
    parts = path.split(".")
    cur: object = obj
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur

VALID_RULE_TYPES = {"required", "type", "min_length", "max_length", "pattern", "range"}

class AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointRequestValidatorV2:
    def __init__(self) -> None:
        self._schemas: dict[tuple[str, str, str], ValidationSchema] = {}

    def register(self, installation_id: str, schema: ValidationSchema) -> ValidationSchema:
        if not installation_id:
            raise ValueError("installation_id is required")
        for r in schema.rules:
            if r.rule_type not in VALID_RULE_TYPES:
                raise ValueError(f"Unknown rule_type: {r.rule_type}")
            if r.rule_type == "pattern":
                re.compile(r.value)  # validate regex at registration
        key = (installation_id, schema.endpoint_path, schema.method.upper())
        self._schemas[key] = schema
        return schema

    def validate(self, installation_id: str, endpoint_path: str, method: str, body: dict) -> ValidationResult:
        schema = self._schemas.get((installation_id, endpoint_path, method.upper()))
        if not schema:
            return ValidationResult(valid=True)
        errors: list[str] = []
        for rule in schema.rules:
            val = _get_nested(body, rule.field_path)
            msg = rule.message or f"{rule.field_path}: {rule.rule_type} failed"
            if rule.rule_type == "required" and val is None:
                errors.append(msg)
            elif rule.rule_type == "type" and val is not None:
                type_map = {"string": str, "integer": int, "boolean": bool, "list": list, "object": dict}
                expected = type_map.get(rule.value)
                if expected == int and isinstance(val, bool):
                    errors.append(msg)
                elif expected and not isinstance(val, expected):
                    errors.append(msg)
            elif rule.rule_type == "min_length" and isinstance(val, str):
                if len(val) < int(rule.value):
                    errors.append(msg)
            elif rule.rule_type == "max_length" and isinstance(val, str):
                if len(val) > int(rule.value):
                    errors.append(msg)
            elif rule.rule_type == "pattern" and isinstance(val, str):
                if not re.fullmatch(rule.value, val):
                    errors.append(msg)
            elif rule.rule_type == "range" and isinstance(val, (int, float)) and not isinstance(val, bool):
                parts = rule.value.split(",")
                if len(parts) == 2:
                    lo, hi = float(parts[0]), float(parts[1])
                    if not (lo <= val <= hi):
                        errors.append(msg)
        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def list_schemas(self, installation_id: str) -> list[ValidationSchema]:
        return [s for (inst, _, _), s in self._schemas.items() if inst == installation_id]
