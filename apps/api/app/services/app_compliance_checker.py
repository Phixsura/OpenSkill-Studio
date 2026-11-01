"""App Compliance Checker — validate apps against compliance policies.

Checks installed apps against organizational compliance rules:
- Define compliance rules (required fields, banned patterns, size limits)
- Run checks against app manifests
- Track compliance status per installation
- Generate compliance reports
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ComplianceRule:
    """A single compliance rule."""

    rule_id: str
    name: str
    description: str
    check_type: str  # "required_field", "banned_pattern", "max_size", "custom"
    target: str      # field name, pattern, etc.
    severity: str = "error"  # "error" or "warning"


@dataclass
class ComplianceViolation:
    """A compliance violation."""

    rule_id: str
    rule_name: str
    message: str
    severity: str
    field: str = ""


@dataclass
class ComplianceReport:
    """Result of compliance checks."""

    installation_id: str
    violations: list[ComplianceViolation]
    rules_checked: int
    compliant: bool
    error_count: int = 0
    warning_count: int = 0


class AppComplianceChecker:
    """Validate apps against compliance policies."""

    def __init__(self) -> None:
        self._rules: list[ComplianceRule] = []

    def add_rule(self, rule: ComplianceRule) -> None:
        """Add a compliance rule."""
        if not rule.rule_id:
            raise ValueError("rule_id is required")
        # No duplicates
        for existing in self._rules:
            if existing.rule_id == rule.rule_id:
                raise ValueError(f"Rule {rule.rule_id} already exists")
        self._rules.append(rule)

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule. Returns True if found."""
        before = len(self._rules)
        self._rules = [r for r in self._rules if r.rule_id != rule_id]
        return len(self._rules) < before

    def check(self, installation_id: str, manifest: dict) -> ComplianceReport:
        """Check a manifest against all rules."""
        if not installation_id:
            raise ValueError("installation_id is required")

        violations: list[ComplianceViolation] = []

        for rule in self._rules:
            v = self._check_rule(rule, manifest)
            if v:
                violations.append(v)

        errors = sum(1 for v in violations if v.severity == "error")
        warnings = sum(1 for v in violations if v.severity == "warning")

        return ComplianceReport(
            installation_id=installation_id,
            violations=violations,
            rules_checked=len(self._rules),
            compliant=errors == 0,
            error_count=errors,
            warning_count=warnings,
        )

    def list_rules(self) -> list[ComplianceRule]:
        return list(self._rules)

    def _check_rule(self, rule: ComplianceRule, manifest: dict) -> ComplianceViolation | None:
        if rule.check_type == "required_field":
            if rule.target not in manifest or not manifest[rule.target]:
                return ComplianceViolation(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    message=f"Required field '{rule.target}' is missing or empty",
                    severity=rule.severity,
                    field=rule.target,
                )

        elif rule.check_type == "banned_pattern":
            for key, value in manifest.items():
                if isinstance(value, str) and re.search(rule.target, value):
                    return ComplianceViolation(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        message=f"Banned pattern found in '{key}'",
                        severity=rule.severity,
                        field=key,
                    )

        elif rule.check_type == "max_size":
            field_name, max_str = rule.target.split(":", 1) if ":" in rule.target else (rule.target, "0")
            max_val = int(max_str) if max_str.isdigit() else 0
            value = manifest.get(field_name)
            if isinstance(value, str) and len(value) > max_val:
                return ComplianceViolation(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    message=f"Field '{field_name}' exceeds max size {max_val}",
                    severity=rule.severity,
                    field=field_name,
                )

        return None
