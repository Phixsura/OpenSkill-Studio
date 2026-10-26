"""Webhook Validator — validate incoming webhook payloads against schemas.

Validates webhook payloads with JSON Schema, content-type checking,
payload size limits, required headers, and detailed error reporting.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field


@dataclass
class WebhookSchema:
    event_type: str
    required_fields: list[str] = field(default_factory=list)
    field_types: dict[str, str] = field(default_factory=dict)  # field -> type
    max_payload_bytes: int = 1024 * 1024  # 1MB default
    required_headers: list[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    parsed_payload: dict | None = None


class WebhookValidatorService:
    """Validates webhook payloads against registered schemas."""

    def __init__(self):
        self._schemas: dict[str, WebhookSchema] = {}

    def register_schema(self, event_type: str, required_fields: list[str] | None = None,
                        field_types: dict[str, str] | None = None,
                        max_payload_bytes: int = 1024 * 1024,
                        required_headers: list[str] | None = None) -> WebhookSchema:
        schema = WebhookSchema(
            event_type=event_type,
            required_fields=required_fields or [],
            field_types=field_types or {},
            max_payload_bytes=max_payload_bytes,
            required_headers=required_headers or [],
        )
        self._schemas[event_type] = schema
        return schema

    def validate(self, event_type: str, payload: str,
                 headers: dict[str, str] | None = None,
                 content_type: str = "application/json") -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        schema = self._schemas.get(event_type)
        if not schema:
            return ValidationResult(valid=False, errors=[f"Unknown event type: {event_type}"])

        # Content type check
        if "json" not in content_type.lower():
            errors.append(f"Invalid content-type: {content_type} (expected application/json)")

        # Payload size check
        payload_size = len(payload.encode("utf-8"))
        if payload_size > schema.max_payload_bytes:
            errors.append(f"Payload too large: {payload_size} bytes (max {schema.max_payload_bytes})")

        if payload_size == 0:
            errors.append("Empty payload")
            return ValidationResult(valid=False, errors=errors)

        # Parse JSON
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as e:
            return ValidationResult(valid=False, errors=[f"Invalid JSON: {e}"])

        if not isinstance(parsed, dict):
            return ValidationResult(valid=False, errors=["Payload must be a JSON object"])

        # Required fields
        for field_name in schema.required_fields:
            if field_name not in parsed:
                errors.append(f"Missing required field: {field_name}")

        # Type checking
        type_map = {"string": str, "integer": int, "boolean": bool, "array": list, "object": dict}
        for field_name, expected in schema.field_types.items():
            if field_name in parsed:
                expected_type = type_map.get(expected)
                if expected_type and not isinstance(parsed[field_name], expected_type):
                    actual = type(parsed[field_name]).__name__
                    errors.append(f"{field_name}: expected {expected}, got {actual}")

        # Required headers
        headers = headers or {}
        for h in schema.required_headers:
            if h not in headers:
                errors.append(f"Missing required header: {h}")

        # Warnings for empty strings
        for field_name in schema.required_fields:
            if field_name in parsed and parsed[field_name] == "":
                warnings.append(f"{field_name} is empty")

        return ValidationResult(
            valid=len(errors) == 0, errors=errors,
            warnings=warnings, parsed_payload=parsed if not errors else None,
        )

    def list_schemas(self) -> list[str]:
        return sorted(self._schemas.keys())
