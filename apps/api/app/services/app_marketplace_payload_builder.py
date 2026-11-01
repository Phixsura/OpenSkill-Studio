"""Payload Builder — construct typed webhook payloads for marketplace events.

Provides builder patterns for creating consistent, versioned webhook
payloads with required fields, timestamps, and metadata.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib


@dataclass
class WebhookPayload:
    event_type: str
    version: str
    data: dict
    metadata: dict = field(default_factory=dict)
    timestamp: str = ""
    idempotency_key: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if not self.idempotency_key:
            raw = f"{self.event_type}:{self.timestamp}:{id(self)}"
            self.idempotency_key = hashlib.sha256(raw.encode()).hexdigest()[:16]


class PayloadBuilder:
    """Fluent builder for constructing webhook payloads."""

    def __init__(self, event_type: str, version: str = "1.0"):
        self._event_type = event_type
        self._version = version
        self._data: dict = {}
        self._metadata: dict = {}

    def set(self, key: str, value: object) -> "PayloadBuilder":
        self._data[key] = value
        return self

    def set_many(self, fields: dict) -> "PayloadBuilder":
        self._data.update(fields)
        return self

    def meta(self, key: str, value: str) -> "PayloadBuilder":
        self._metadata[key] = value
        return self

    def build(self) -> WebhookPayload:
        return WebhookPayload(
            event_type=self._event_type, version=self._version,
            data=dict(self._data), metadata=dict(self._metadata),
        )


class PayloadRegistry:
    """Registry of payload schemas for validation."""

    def __init__(self):
        self._schemas: dict[str, dict] = {}

    def register(self, event_type: str, required_fields: list[str],
                 optional_fields: list[str] | None = None) -> None:
        self._schemas[event_type] = {
            "required": set(required_fields),
            "optional": set(optional_fields or []),
        }

    def validate(self, payload: WebhookPayload) -> tuple[bool, list[str]]:
        schema = self._schemas.get(payload.event_type)
        if not schema:
            return True, []  # no schema = pass
        missing = schema["required"] - set(payload.data.keys())
        if missing:
            return False, [f"Missing required field: {f}" for f in sorted(missing)]
        unknown = set(payload.data.keys()) - schema["required"] - schema["optional"]
        warnings = [f"Unknown field: {f}" for f in sorted(unknown)] if unknown else []
        return True, warnings

    def get_schema(self, event_type: str) -> dict | None:
        return self._schemas.get(event_type)

    def list_event_types(self) -> list[str]:
        return sorted(self._schemas.keys())
