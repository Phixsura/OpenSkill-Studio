"""App API Webhook Payload Schema — validate webhook payloads against schemas.

Manages payload schemas:
- Define schemas per event type
- Validate payloads against registered schemas
- Track validation pass/fail
- Per-installation scoped schemas
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class PayloadSchema:
    """A webhook payload schema."""

    event_type: str
    required_fields: list[str]
    optional_fields: list[str] = field(default_factory=list)
    validations: int = 0
    failures: int = 0

    @property
    def pass_rate(self) -> float:
        if self.validations == 0:
            return 100.0
        return round((self.validations - self.failures) / self.validations * 100, 1)


class AppAPIWebhookPayloadSchema:
    """Validate webhook payloads against schemas."""

    def __init__(self) -> None:
        self._schemas: dict[tuple[str, str], PayloadSchema] = {}

    def define(
        self, installation_id: str, event_type: str,
        required_fields: list[str], optional_fields: list[str] | None = None,
    ) -> PayloadSchema:
        if not installation_id:
            raise ValueError("installation_id is required")
        schema = PayloadSchema(
            event_type=event_type, required_fields=required_fields,
            optional_fields=optional_fields or [],
        )
        self._schemas[(installation_id, event_type)] = schema
        return schema

    def validate(self, installation_id: str, event_type: str, payload: dict) -> list[str]:
        """Validate payload. Returns list of error messages."""
        key = (installation_id, event_type)
        schema = self._schemas.get(key)
        if schema is None:
            raise KeyError(f"No schema for event type {event_type}")

        schema.validations += 1
        errors: list[str] = []
        for f in schema.required_fields:
            if f not in payload:
                errors.append(f"Missing required field: {f}")

        allowed = set(schema.required_fields) | set(schema.optional_fields)
        for f in payload:
            if f not in allowed:
                errors.append(f"Unknown field: {f}")

        if errors:
            schema.failures += 1
        return errors

    def list_schemas(self, installation_id: str) -> list[PayloadSchema]:
        return [s for (inst, _), s in self._schemas.items() if inst == installation_id]
