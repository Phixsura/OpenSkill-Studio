"""App Traffic Mirror — duplicate traffic to shadow environments for testing.

Manages traffic mirroring for installed apps:
- Define mirror rules (source → shadow target)
- Track mirrored request counts
- Enable/disable mirrors
- Compare response divergence
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class MirrorRule:
    """A traffic mirroring rule."""

    rule_id: str
    source_path: str
    shadow_target: str
    sample_rate: float = 1.0  # 0.0-1.0
    enabled: bool = True
    mirrored_count: int = 0
    divergence_count: int = 0
    created_at: float = field(default_factory=time.time)


class AppTrafficMirror:
    """Duplicate traffic to shadow environments."""

    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], MirrorRule] = {}

    def add_rule(
        self,
        installation_id: str,
        rule_id: str,
        source_path: str,
        shadow_target: str,
        sample_rate: float = 1.0,
    ) -> MirrorRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not rule_id:
            raise ValueError("rule_id is required")
        if not source_path or not shadow_target:
            raise ValueError("source_path and shadow_target are required")
        if not 0.0 < sample_rate <= 1.0:
            raise ValueError("sample_rate must be between 0 and 1")

        key = (installation_id, rule_id)
        if key in self._rules:
            raise ValueError(f"Rule {rule_id} already exists")

        rule = MirrorRule(
            rule_id=rule_id, source_path=source_path,
            shadow_target=shadow_target, sample_rate=sample_rate,
        )
        self._rules[key] = rule
        return rule

    def record_mirror(
        self, installation_id: str, rule_id: str, diverged: bool = False
    ) -> MirrorRule:
        rule = self._get(installation_id, rule_id)
        rule.mirrored_count += 1
        if diverged:
            rule.divergence_count += 1
        return rule

    def enable_rule(self, installation_id: str, rule_id: str) -> MirrorRule:
        rule = self._get(installation_id, rule_id)
        rule.enabled = True
        return rule

    def disable_rule(self, installation_id: str, rule_id: str) -> MirrorRule:
        rule = self._get(installation_id, rule_id)
        rule.enabled = False
        return rule

    def get_divergence_rate(self, installation_id: str, rule_id: str) -> float:
        rule = self._get(installation_id, rule_id)
        if rule.mirrored_count == 0:
            return 0.0
        return round(rule.divergence_count / rule.mirrored_count * 100, 2)

    def list_rules(self, installation_id: str) -> list[MirrorRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id]

    def _get(self, installation_id: str, rule_id: str) -> MirrorRule:
        key = (installation_id, rule_id)
        rule = self._rules.get(key)
        if rule is None:
            raise KeyError(f"Rule {rule_id} not found")
        return rule
