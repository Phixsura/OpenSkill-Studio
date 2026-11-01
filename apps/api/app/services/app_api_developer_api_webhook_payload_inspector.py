"""App API Developer Webhook Payload Inspector — inspect and validate payloads."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import structlog

log = structlog.get_logger()

@dataclass
class PayloadInspection:
    inspection_id: str
    event_type: str
    payload_size_bytes: int
    field_count: int
    has_nested: bool
    content_type: str = "application/json"
    validation_errors: list[str] = field(default_factory=list)

class AppAPIDeveloperAPIWebhookPayloadInspector:
    def __init__(self, max_payload_bytes: int = 1_048_576) -> None:
        self._max = max_payload_bytes
        self._inspections: dict[str, list[PayloadInspection]] = {}

    def inspect(self, installation_id: str, inspection_id: str, event_type: str, payload: str) -> PayloadInspection:
        if not installation_id: raise ValueError("installation_id is required")
        errors: list[str] = []
        size = len(payload.encode("utf-8"))
        if size > self._max:
            errors.append(f"Payload exceeds max size ({size} > {self._max})")
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            errors.append("Invalid JSON")
            parsed = {}
        field_count = len(parsed) if isinstance(parsed, dict) else 0
        has_nested = any(isinstance(v, (dict, list)) for v in parsed.values()) if isinstance(parsed, dict) else False
        insp = PayloadInspection(inspection_id=inspection_id, event_type=event_type, payload_size_bytes=size, field_count=field_count, has_nested=has_nested, validation_errors=errors)
        self._inspections.setdefault(installation_id, []).append(insp)
        return insp

    def recent(self, installation_id: str, limit: int = 20) -> list[PayloadInspection]:
        return list(reversed(self._inspections.get(installation_id, [])[-limit:]))

    def with_errors(self, installation_id: str) -> list[PayloadInspection]:
        return [i for i in self._inspections.get(installation_id, []) if i.validation_errors]
