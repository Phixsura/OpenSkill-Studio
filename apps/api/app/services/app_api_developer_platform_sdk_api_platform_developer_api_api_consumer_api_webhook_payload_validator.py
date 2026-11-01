"""API Consumer Webhook Payload Validator — validate outgoing webhook payloads."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import structlog

log = structlog.get_logger()

@dataclass
class PayloadValidation:
    valid: bool
    errors: list[str] = field(default_factory=list)
    payload_size_bytes: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookPayloadValidator:
    def __init__(self, max_payload_bytes: int = 1048576) -> None:
        self._max_bytes = max(1024, max_payload_bytes)
        self._stats: dict[str, dict[str, int]] = {}

    def validate(self, installation_id: str, payload: str, event_type: str = "") -> PayloadValidation:
        if not installation_id: raise ValueError("installation_id is required")
        errors: list[str] = []
        size = len(payload.encode("utf-8"))
        if size > self._max_bytes: errors.append(f"Payload too large: {size} > {self._max_bytes}")
        try:
            data = json.loads(payload)
            if not isinstance(data, dict): errors.append("Payload must be a JSON object")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {e}")
        valid = len(errors) == 0
        stats = self._stats.setdefault(installation_id, {"valid": 0, "invalid": 0})
        stats["valid" if valid else "invalid"] += 1
        return PayloadValidation(valid=valid, errors=errors, payload_size_bytes=size)

    def stats(self, installation_id: str) -> dict[str, int]:
        return self._stats.get(installation_id, {"valid": 0, "invalid": 0})

    def validation_rate(self, installation_id: str) -> float:
        s = self.stats(installation_id)
        total = s["valid"] + s["invalid"]
        if total == 0: return 0.0
        return round((s["valid"] / total) * 100, 1)
