"""App Payload Validator — validate webhook payloads against expected schemas.

Validates incoming webhook payloads:
- Register expected schemas per event type
- Validate payloads against schemas
- Track validation success rates
- Per-installation scoped schemas
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class PayloadSchema:
    """Expected schema for a webhook event type."""

    event_type: str
    required_fields: list[str]
    optional_fields: list[str] = field(default_factory=list)


@dataclass
class PayloadValidationResult:
    """Result of validating a webhook payload."""

    event_type: str
    valid: bool
    missing_fields: list[str]
    unknown_fields: list[str]


class AppPayloadValidator:
    """Validate webhook payloads against expected schemas."""

    def __init__(self) -> None:
        # (installation_id, event_type) → PayloadSchema
        self._schemas: dict[tuple[str, str], PayloadSchema] = {}
        # (installation_id, event_type) → (total, passed)
        self._stats: dict[tuple[str, str], tuple[int, int]] = {}

    def register_schema(
        self,
        installation_id: str,
        event_type: str,
        required_fields: list[str],
        optional_fields: list[str] | None = None,
    ) -> PayloadSchema:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not event_type:
            raise ValueError("event_type is required")

        schema = PayloadSchema(
            event_type=event_type,
            required_fields=required_fields,
            optional_fields=optional_fields or [],
        )
        self._schemas[(installation_id, event_type)] = schema
        return schema

    def validate(
        self,
        installation_id: str,
        event_type: str,
        payload: dict,
    ) -> PayloadValidationResult:
        key = (installation_id, event_type)
        schema = self._schemas.get(key)
        if schema is None:
            raise KeyError(f"No schema for event type {event_type}")

        missing = [f for f in schema.required_fields if f not in payload]
        known = set(schema.required_fields) | set(schema.optional_fields)
        unknown = [f for f in payload if f not in known]
        valid = len(missing) == 0

        # Track stats
        total, passed = self._stats.get(key, (0, 0))
        self._stats[key] = (total + 1, passed + (1 if valid else 0))

        return PayloadValidationResult(
            event_type=event_type, valid=valid,
            missing_fields=missing, unknown_fields=unknown,
        )

    def success_rate(self, installation_id: str, event_type: str) -> float:
        key = (installation_id, event_type)
        total, passed = self._stats.get(key, (0, 0))
        return round(passed / total * 100, 1) if total > 0 else 100.0

    def list_schemas(self, installation_id: str) -> list[PayloadSchema]:
        return [s for (inst, _), s in self._schemas.items() if inst == installation_id]
