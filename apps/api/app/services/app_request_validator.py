"""App Request Validator — validate incoming API requests against schemas.

Validates request payloads before processing:
- Required/optional field checks
- Type validation
- String length limits
- Numeric range checks
- Nested object support
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class FieldRule:
    """Validation rule for a field."""

    field: str
    required: bool = True
    field_type: str = "string"  # string, int, float, bool, list, object
    min_length: int | None = None
    max_length: int | None = None
    min_value: float | None = None
    max_value: float | None = None


@dataclass
class ValidationIssue:
    """A validation issue."""

    field: str
    message: str


@dataclass
class RequestValidationResult:
    """Result of validating a request."""

    valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)


TYPE_MAP: dict[str, type | tuple[type, ...]] = {
    "string": str,
    "int": int,
    "float": (int, float),
    "bool": bool,
    "list": list,
    "object": dict,
}


class AppRequestValidator:
    """Validate incoming API requests against schemas."""

    def __init__(self) -> None:
        # (installation_id, schema_id) → list[FieldRule]
        self._schemas: dict[tuple[str, str], list[FieldRule]] = {}

    def define_schema(
        self, installation_id: str, schema_id: str, rules: list[FieldRule]
    ) -> None:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not schema_id:
            raise ValueError("schema_id is required")
        self._schemas[(installation_id, schema_id)] = list(rules)

    def validate(
        self, installation_id: str, schema_id: str, payload: dict
    ) -> RequestValidationResult:
        key = (installation_id, schema_id)
        rules = self._schemas.get(key)
        if rules is None:
            raise KeyError(f"Schema {schema_id} not found")

        issues: list[ValidationIssue] = []
        for rule in rules:
            value = payload.get(rule.field)

            if value is None:
                if rule.required:
                    issues.append(ValidationIssue(rule.field, "Required field missing"))
                continue

            # Type check (bool before int since bool is subclass of int)
            if rule.field_type in ("int", "float") and isinstance(value, bool):
                issues.append(ValidationIssue(rule.field, f"Expected {rule.field_type}, got bool"))
                continue

            expected = TYPE_MAP.get(rule.field_type)
            if expected and not isinstance(value, expected):
                issues.append(ValidationIssue(rule.field, f"Expected {rule.field_type}"))
                continue

            # String length
            if isinstance(value, str):
                if rule.min_length is not None and len(value) < rule.min_length:
                    issues.append(ValidationIssue(rule.field, f"Too short (min {rule.min_length})"))
                if rule.max_length is not None and len(value) > rule.max_length:
                    issues.append(ValidationIssue(rule.field, f"Too long (max {rule.max_length})"))

            # Numeric range
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if rule.min_value is not None and value < rule.min_value:
                    issues.append(ValidationIssue(rule.field, f"Below minimum ({rule.min_value})"))
                if rule.max_value is not None and value > rule.max_value:
                    issues.append(ValidationIssue(rule.field, f"Above maximum ({rule.max_value})"))

        return RequestValidationResult(valid=len(issues) == 0, issues=issues)

    def list_schemas(self, installation_id: str) -> list[str]:
        return [sid for (inst, sid) in self._schemas if inst == installation_id]
