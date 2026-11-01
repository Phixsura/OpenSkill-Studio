"""App API Compliance Check — verify API compliance with standards.

Manages compliance checks:
- Define compliance rules
- Run checks and record results
- Track compliance score
- Per-installation scoped checks
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ComplianceRule:
    """A compliance check rule."""

    rule_id: str
    name: str
    category: str  # "security", "performance", "documentation"
    passed: bool | None = None
    message: str = ""


class AppAPIComplianceCheck:
    """Verify API compliance with standards."""

    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], ComplianceRule] = {}

    def add_rule(
        self, installation_id: str, rule_id: str, name: str, category: str,
    ) -> ComplianceRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        rule = ComplianceRule(rule_id=rule_id, name=name, category=category)
        self._rules[(installation_id, rule_id)] = rule
        return rule

    def record_result(
        self, installation_id: str, rule_id: str, passed: bool, message: str = "",
    ) -> ComplianceRule:
        r = self._get(installation_id, rule_id)
        r.passed = passed
        r.message = message
        return r

    def compliance_score(self, installation_id: str) -> float:
        rules = [r for (inst, _), r in self._rules.items() if inst == installation_id and r.passed is not None]
        if not rules:
            return 100.0
        passed = sum(1 for r in rules if r.passed)
        return round(passed / len(rules) * 100, 1)

    def failing_rules(self, installation_id: str) -> list[ComplianceRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id and r.passed is False]

    def list_rules(self, installation_id: str) -> list[ComplianceRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id]

    def _get(self, installation_id: str, rule_id: str) -> ComplianceRule:
        key = (installation_id, rule_id)
        r = self._rules.get(key)
        if r is None:
            raise KeyError(f"Rule {rule_id} not found")
        return r
