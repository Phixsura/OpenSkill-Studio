"""App Data Masking — mask sensitive fields in API responses.

Manages data masking rules for installed apps:
- Define masking rules per field
- Masking strategies: full, partial, hash, redact
- Apply masks to response payloads
- Per-installation scoped rules
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class MaskRule:
    """A data masking rule."""

    field: str
    strategy: str  # "full", "partial", "hash", "redact"
    visible_chars: int = 4  # for partial masking


class AppDataMasking:
    """Mask sensitive fields in API responses."""

    def __init__(self) -> None:
        # (installation_id, ruleset_id) → list[MaskRule]
        self._rulesets: dict[tuple[str, str], list[MaskRule]] = {}

    def define_rules(
        self,
        installation_id: str,
        ruleset_id: str,
        rules: list[MaskRule],
    ) -> list[MaskRule]:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not ruleset_id:
            raise ValueError("ruleset_id is required")
        for r in rules:
            if r.strategy not in ("full", "partial", "hash", "redact"):
                raise ValueError(f"Invalid strategy: {r.strategy}")
        self._rulesets[(installation_id, ruleset_id)] = list(rules)
        return rules

    def apply_mask(
        self,
        installation_id: str,
        ruleset_id: str,
        data: dict,
    ) -> dict:
        """Apply masking rules to a data dict."""
        key = (installation_id, ruleset_id)
        rules = self._rulesets.get(key)
        if rules is None:
            raise KeyError(f"Ruleset {ruleset_id} not found")

        result = dict(data)
        for rule in rules:
            if rule.field in result:
                result[rule.field] = self._mask_value(str(result[rule.field]), rule)
        return result

    def apply_mask_batch(
        self, installation_id: str, ruleset_id: str, records: list[dict]
    ) -> list[dict]:
        return [self.apply_mask(installation_id, ruleset_id, r) for r in records]

    def _mask_value(self, value: str, rule: MaskRule) -> str:
        if rule.strategy == "full":
            return "***"
        if rule.strategy == "partial":
            if len(value) <= rule.visible_chars:
                return "***"
            return value[:rule.visible_chars] + "***"
        if rule.strategy == "hash":
            return hashlib.sha256(value.encode()).hexdigest()[:12]
        if rule.strategy == "redact":
            return "[REDACTED]"
        return value
