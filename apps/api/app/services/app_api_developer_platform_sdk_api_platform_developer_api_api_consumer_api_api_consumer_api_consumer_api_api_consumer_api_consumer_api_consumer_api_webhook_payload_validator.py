"""Consumer API Webhook Payload Validator — validate outgoing webhook payloads."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import structlog

log = structlog.get_logger()

@dataclass
class PayloadRule:
    field_path: str
    rule_type: str  # "required", "type", "max_length", "pattern"
    value: str = ""

@dataclass
class PayloadSchema:
    schema_id: str
    event_type: str
    rules: list[PayloadRule] = field(default_factory=list)

@dataclass
class PayloadValidationResult:
    valid: bool
    event_type: str
    errors: list[str] = field(default_factory=list)
    payload_size_bytes: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiWebhookPayloadValidator:
    def __init__(self, max_payload_bytes: int = 1048576) -> None:
        self._schemas: dict[tuple[str, str], PayloadSchema] = {}
        self._max_bytes = max_payload_bytes

    def register_schema(self, installation_id: str, schema: PayloadSchema) -> PayloadSchema:
        if not installation_id:
            raise ValueError("installation_id is required")
        self._schemas[(installation_id, schema.event_type)] = schema
        return schema

    def validate(self, installation_id: str, event_type: str, payload: dict) -> PayloadValidationResult:
        payload_str = json.dumps(payload, default=str)
        size = len(payload_str.encode())
        if size > self._max_bytes:
            return PayloadValidationResult(valid=False, event_type=event_type, errors=[f"Payload exceeds max size ({size} > {self._max_bytes})"], payload_size_bytes=size)
        schema = self._schemas.get((installation_id, event_type))
        if not schema:
            return PayloadValidationResult(valid=True, event_type=event_type, payload_size_bytes=size)
        errors: list[str] = []
        for rule in schema.rules:
            val = payload.get(rule.field_path)
            if rule.rule_type == "required" and val is None:
                errors.append(f"{rule.field_path}: required")
            elif rule.rule_type == "type" and val is not None:
                type_checks = {"string": str, "integer": int, "boolean": bool, "list": list, "object": dict}
                expected = type_checks.get(rule.value)
                if expected == int and isinstance(val, bool):
                    errors.append(f"{rule.field_path}: expected integer, got boolean")
                elif expected and not isinstance(val, expected):
                    errors.append(f"{rule.field_path}: expected {rule.value}")
            elif rule.rule_type == "max_length" and isinstance(val, str):
                if len(val) > int(rule.value):
                    errors.append(f"{rule.field_path}: exceeds max length {rule.value}")
        return PayloadValidationResult(valid=len(errors) == 0, event_type=event_type, errors=errors, payload_size_bytes=size)

    def list_schemas(self, installation_id: str) -> list[PayloadSchema]:
        return [s for (inst, _), s in self._schemas.items() if inst == installation_id]
