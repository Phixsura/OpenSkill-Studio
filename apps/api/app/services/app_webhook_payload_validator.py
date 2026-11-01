"""App Webhook Payload Validator — validate outbound webhook payloads against event schemas.

Ensures webhook payloads conform to the declared event schema before delivery:
- Required field validation
- Type checking (string, number, boolean, array, object)
- Max payload size enforcement
- Nested object validation
- Null/missing field detection
- Schema-to-payload conformance report
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()

MAX_PAYLOAD_BYTES = 256 * 1024  # 256KB


class ValidationSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass
class PayloadIssue:
    """A single validation issue."""

    field_path: str
    severity: ValidationSeverity
    message: str


@dataclass
class PayloadValidationResult:
    """Result of validating a webhook payload."""

    valid: bool
    issues: list[PayloadIssue]
    payload_bytes: int
    fields_checked: int

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == ValidationSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == ValidationSeverity.WARNING)


@dataclass
class FieldSpec:
    """Schema specification for a single payload field."""

    name: str
    field_type: str       # "string", "number", "boolean", "array", "object", "any"
    required: bool = True
    nullable: bool = False
    children: dict[str, FieldSpec] | None = None  # for nested objects


TYPE_CHECKS = {
    "string": lambda v: isinstance(v, str),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
    "any": lambda _: True,
}


class AppWebhookPayloadValidator:
    """Validate webhook payloads against field specs."""

    def validate(self, payload: dict, schema: list[FieldSpec],
                 event_type: str = "") -> PayloadValidationResult:
        """Validate a payload dict against the schema spec."""
        issues: list[PayloadIssue] = []
        fields_checked = 0

        # Size check
        try:
            payload_bytes = len(json.dumps(payload, default=str).encode("utf-8"))
        except (TypeError, ValueError):
            payload_bytes = 0
            issues.append(PayloadIssue("$", ValidationSeverity.ERROR,
                                        "Payload is not JSON-serializable"))
            return PayloadValidationResult(False, issues, payload_bytes, 0)

        if payload_bytes > MAX_PAYLOAD_BYTES:
            issues.append(PayloadIssue("$", ValidationSeverity.ERROR,
                                        f"Payload size {payload_bytes} bytes exceeds {MAX_PAYLOAD_BYTES} limit"))

        # Field validation
        for spec in schema:
            field_issues, checked = self._validate_field(payload, spec, "")
            issues.extend(field_issues)
            fields_checked += checked

        # Extra fields warning
        declared = {s.name for s in schema}
        for key in payload:
            if key not in declared:
                issues.append(PayloadIssue(key, ValidationSeverity.WARNING,
                                            f"Undeclared field '{key}' in payload"))

        valid = not any(i.severity == ValidationSeverity.ERROR for i in issues)
        return PayloadValidationResult(valid, issues, payload_bytes, fields_checked)

    def _validate_field(self, data: dict, spec: FieldSpec,
                        prefix: str) -> tuple[list[PayloadIssue], int]:
        issues: list[PayloadIssue] = []
        path = f"{prefix}.{spec.name}" if prefix else spec.name
        checked = 1

        value = data.get(spec.name)

        # Missing check
        if value is None:
            if spec.required and not spec.nullable:
                issues.append(PayloadIssue(path, ValidationSeverity.ERROR,
                                            f"Required field '{spec.name}' is missing"))
            return issues, checked

        # Null check
        if value is None and not spec.nullable:
            issues.append(PayloadIssue(path, ValidationSeverity.ERROR,
                                        f"Field '{spec.name}' cannot be null"))
            return issues, checked

        # Type check
        type_fn = TYPE_CHECKS.get(spec.field_type)
        if type_fn and not type_fn(value):
            issues.append(PayloadIssue(path, ValidationSeverity.ERROR,
                                        f"Expected {spec.field_type}, got {type(value).__name__}"))
            return issues, checked

        # Nested object validation
        if spec.children and isinstance(value, dict):
            for child_spec in spec.children.values():
                child_issues, child_checked = self._validate_field(value, child_spec, path)
                issues.extend(child_issues)
                checked += child_checked

        return issues, checked
