"""App API Developer Webhook Payload Validator — validate outbound webhook payloads."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import structlog

log = structlog.get_logger()

@dataclass
class PayloadValidation:
    destination: str
    total_validated: int = 0
    valid_count: int = 0
    invalid_count: int = 0
    last_error: str = ""

    @property
    def valid_rate(self) -> float:
        return round(self.valid_count / self.total_validated * 100, 1) if self.total_validated > 0 else 100.0

class AppAPIDeveloperPlatformSDKApiWebhookPayloadValidator:
    def __init__(self, max_payload_bytes: int = 1_048_576) -> None:
        self._max_bytes = max_payload_bytes
        self._validations: dict[tuple[str, str], PayloadValidation] = {}

    def validate(self, installation_id: str, destination: str, payload: str) -> tuple[bool, str]:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, destination)
        if key not in self._validations:
            self._validations[key] = PayloadValidation(destination=destination)
        v = self._validations[key]
        v.total_validated += 1
        # Check size
        size = len(payload.encode("utf-8"))
        if size > self._max_bytes:
            v.invalid_count += 1
            v.last_error = f"Payload too large: {size} bytes"
            return (False, v.last_error)
        # Check JSON validity
        try:
            json.loads(payload)
        except json.JSONDecodeError as e:
            v.invalid_count += 1
            v.last_error = f"Invalid JSON: {str(e)[:100]}"
            return (False, v.last_error)
        v.valid_count += 1
        return (True, "")

    def stats(self, installation_id: str, destination: str) -> PayloadValidation | None:
        return self._validations.get((installation_id, destination))

    def invalid_destinations(self, installation_id: str) -> list[PayloadValidation]:
        return [v for (inst, _), v in self._validations.items() if inst == installation_id and v.invalid_count > 0]

    def all_validations(self, installation_id: str) -> list[PayloadValidation]:
        return [v for (inst, _), v in self._validations.items() if inst == installation_id]
