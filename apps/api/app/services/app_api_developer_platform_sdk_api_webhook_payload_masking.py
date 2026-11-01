"""App API Developer Webhook Payload Masking — mask sensitive fields in payloads."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

_DEFAULT_SENSITIVE = {"password", "secret", "token", "api_key", "credit_card", "ssn", "authorization"}

@dataclass
class MaskingRule:
    field_pattern: str
    mask_char: str = "*"
    visible_chars: int = 4  # keep last N chars visible

@dataclass
class MaskingConfig:
    destination: str
    rules: list[MaskingRule] = field(default_factory=list)
    masked_count: int = 0

class AppAPIDeveloperPlatformSDKApiWebhookPayloadMasking:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], MaskingConfig] = {}

    def configure(self, installation_id: str, destination: str, rules: list[dict]) -> MaskingConfig:
        if not installation_id: raise ValueError("installation_id is required")
        parsed = []
        for r in rules:
            vc = int(r.get("visible_chars", 4))
            if vc < 0: raise ValueError("visible_chars must be >= 0")
            parsed.append(MaskingRule(field_pattern=r["field_pattern"], mask_char=r.get("mask_char", "*"), visible_chars=vc))
        key = (installation_id, destination)
        c = MaskingConfig(destination=destination, rules=parsed)
        self._configs[key] = c
        return c

    def mask(self, installation_id: str, destination: str, payload: dict) -> dict:
        key = (installation_id, destination)
        c = self._configs.get(key)
        if c is None:
            return self._default_mask(payload)
        result = dict(payload)
        for field_name, value in payload.items():
            for rule in c.rules:
                if re.search(rule.field_pattern, field_name, re.IGNORECASE):
                    if isinstance(value, str) and len(value) > rule.visible_chars:
                        visible = value[-rule.visible_chars:] if rule.visible_chars > 0 else ""
                        result[field_name] = rule.mask_char * (len(value) - rule.visible_chars) + visible
                    else:
                        result[field_name] = "[MASKED]"
                    c.masked_count += 1
                    break
        return result

    def _default_mask(self, payload: dict) -> dict:
        result = dict(payload)
        for k, v in payload.items():
            if k.lower() in _DEFAULT_SENSITIVE:
                result[k] = "[MASKED]"
        return result

    def all_configs(self, installation_id: str) -> list[MaskingConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
