"""Endpoint Compliance Checker — regulatory compliance validation."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

FRAMEWORKS = ("gdpr", "hipaa", "soc2", "pci_dss", "ccpa", "iso27001")


@dataclass
class ComplianceRule:
    rule_id: str
    framework: str
    name: str
    description: str = ""
    severity: str = "high"  # critical, high, medium, low
    auto_check: bool = True


@dataclass
class CheckResult:
    rule_id: str
    endpoint_id: str
    passed: bool
    details: str = ""


@dataclass
class ComplianceChecker:
    """Validate endpoint compliance against regulatory frameworks."""

    _rules: dict[str, ComplianceRule] = field(default_factory=dict)
    _results: dict[str, list[CheckResult]] = field(default_factory=dict)  # endpoint -> results

    def add_rule(self, rule: ComplianceRule) -> dict:
        if rule.framework not in FRAMEWORKS:
            raise ValueError(f"Unknown framework: {rule.framework}")
        if rule.rule_id in self._rules:
            raise ValueError(f"Rule {rule.rule_id} already exists")
        self._rules[rule.rule_id] = rule
        logger.info("compliance_rule_added", rule_id=rule.rule_id)
        return {"rule_id": rule.rule_id, "framework": rule.framework}

    def check(self, endpoint_id: str, rule_id: str, passed: bool, details: str = "") -> dict:
        if rule_id not in self._rules:
            raise ValueError(f"Rule {rule_id} not found")
        result = CheckResult(rule_id=rule_id, endpoint_id=endpoint_id,
                              passed=passed, details=details)
        self._results.setdefault(endpoint_id, []).append(result)
        rule = self._rules[rule_id]
        if not passed:
            logger.warning("compliance_violation", endpoint_id=endpoint_id,
                           rule_id=rule_id, framework=rule.framework)
        return {"endpoint_id": endpoint_id, "rule_id": rule_id,
                "passed": passed, "framework": rule.framework}

    def get_endpoint_compliance(self, endpoint_id: str) -> dict:
        results = self._results.get(endpoint_id, [])
        if not results:
            return {"endpoint_id": endpoint_id, "status": "unchecked"}
        # Latest result per rule
        latest: dict[str, CheckResult] = {}
        for r in results:
            latest[r.rule_id] = r
        total = len(latest)
        passed = sum(1 for r in latest.values() if r.passed)
        violations = [
            {"rule_id": r.rule_id, "framework": self._rules[r.rule_id].framework,
             "name": self._rules[r.rule_id].name, "severity": self._rules[r.rule_id].severity,
             "details": r.details}
            for r in latest.values() if not r.passed and r.rule_id in self._rules
        ]
        violations.sort(key=lambda v: ["critical", "high", "medium", "low"].index(v["severity"]))
        score = round(passed / total * 100, 1) if total > 0 else 0
        status = "compliant" if score == 100 else "partial" if score >= 80 else "non_compliant"
        return {
            "endpoint_id": endpoint_id, "status": status, "score": score,
            "rules_checked": total, "passed": passed,
            "violations": violations,
        }

    def get_framework_summary(self, framework: str) -> dict:
        rules = [r for r in self._rules.values() if r.framework == framework]
        rule_ids = {r.rule_id for r in rules}
        all_results: dict[str, bool] = {}
        for ep_results in self._results.values():
            for r in ep_results:
                if r.rule_id in rule_ids:
                    all_results[r.rule_id] = r.passed
        checked = len(all_results)
        passed = sum(1 for v in all_results.values() if v)
        return {
            "framework": framework,
            "total_rules": len(rules),
            "checked": checked,
            "passed": passed,
            "failed": checked - passed,
        }

    def list_rules(self, framework: str | None = None) -> list[dict]:
        rules = list(self._rules.values())
        if framework:
            rules = [r for r in rules if r.framework == framework]
        return [{"rule_id": r.rule_id, "framework": r.framework,
                 "name": r.name, "severity": r.severity}
                for r in rules]

    def get_stats(self) -> dict:
        all_checks = sum(len(r) for r in self._results.values())
        violations = sum(1 for results in self._results.values()
                         for r in results if not r.passed)
        return {
            "total_rules": len(self._rules),
            "endpoints_checked": len(self._results),
            "total_checks": all_checks,
            "total_violations": violations,
        }
