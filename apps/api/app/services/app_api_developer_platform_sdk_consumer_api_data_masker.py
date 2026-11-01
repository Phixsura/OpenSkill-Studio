"""Consumer API Data Masker — PII/sensitive data masking engine."""
from __future__ import annotations

import re
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class MaskRule:
    rule_id: str
    field_pattern: str  # regex or exact field name
    mask_type: str  # full, partial, hash, redact
    replacement: str = "***"


@dataclass
class DataMasker:
    """Mask sensitive/PII data in API responses."""

    _rules: dict[str, MaskRule] = field(default_factory=dict)
    _masked_count: int = 0

    def add_rule(self, rule: MaskRule) -> dict:
        if rule.rule_id in self._rules:
            raise ValueError(f"Rule {rule.rule_id} already exists")
        if rule.mask_type not in ("full", "partial", "hash", "redact"):
            raise ValueError(f"Invalid mask_type: {rule.mask_type}")
        self._rules[rule.rule_id] = rule
        logger.info("mask_rule_added", rule_id=rule.rule_id)
        return {"rule_id": rule.rule_id, "field_pattern": rule.field_pattern}

    def remove_rule(self, rule_id: str) -> dict:
        if rule_id in self._rules:
            del self._rules[rule_id]
            return {"removed": True}
        return {"removed": False}

    def _apply_mask(self, value: str, mask_type: str, replacement: str) -> str:
        if mask_type == "full":
            return replacement
        elif mask_type == "partial":
            if len(value) <= 4:
                return replacement
            return value[:2] + "*" * (len(value) - 4) + value[-2:]
        elif mask_type == "hash":
            import hashlib
            return hashlib.sha256(value.encode()).hexdigest()[:16]
        elif mask_type == "redact":
            return "[REDACTED]"
        return value

    def mask(self, data: dict) -> dict:
        result = dict(data)
        fields_masked = []
        for key in list(result.keys()):
            for rule in self._rules.values():
                try:
                    if re.fullmatch(rule.field_pattern, key):
                        val = result[key]
                        if isinstance(val, str):
                            result[key] = self._apply_mask(val, rule.mask_type, rule.replacement)
                            fields_masked.append(key)
                            self._masked_count += 1
                        break
                except re.error:
                    if rule.field_pattern == key:
                        val = result[key]
                        if isinstance(val, str):
                            result[key] = self._apply_mask(val, rule.mask_type, rule.replacement)
                            fields_masked.append(key)
                            self._masked_count += 1
                        break
        return {"data": result, "fields_masked": fields_masked}

    def mask_nested(self, data: dict, prefix: str = "") -> dict:
        result = {}
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result[key] = self.mask_nested(value, full_key)["data"]
            else:
                masked = self.mask({key: value})
                result[key] = masked["data"][key]
        return {"data": result}

    def list_rules(self) -> list[dict]:
        return [
            {"rule_id": r.rule_id, "field_pattern": r.field_pattern,
             "mask_type": r.mask_type}
            for r in self._rules.values()
        ]

    def get_stats(self) -> dict:
        return {
            "total_rules": len(self._rules),
            "total_masked": self._masked_count,
        }
