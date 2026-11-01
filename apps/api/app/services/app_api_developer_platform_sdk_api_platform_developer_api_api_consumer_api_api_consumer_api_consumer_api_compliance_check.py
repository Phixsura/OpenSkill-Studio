"""Consumer API Compliance Check — verify consumer API usage meets compliance requirements."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class ComplianceRule:
    rule_id: str
    name: str
    category: str  # "data_privacy", "security", "rate_limiting", "authentication", "logging"
    description: str = ""
    severity: str = "warning"  # "info", "warning", "critical"

@dataclass
class ComplianceResult:
    rule_id: str
    rule_name: str
    passed: bool
    severity: str
    details: str = ""

@dataclass
class ComplianceReport:
    consumer_id: str
    checked_at: datetime
    results: list[ComplianceResult] = field(default_factory=list)
    passed: int = 0
    failed: int = 0
    score: float = 0.0  # 0-100

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiComplianceCheck:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], ComplianceRule] = {}
        self._reports: dict[tuple[str, str], list[ComplianceReport]] = {}

    def add_rule(self, installation_id: str, rule: ComplianceRule) -> ComplianceRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if rule.category not in ("data_privacy", "security", "rate_limiting", "authentication", "logging"):
            raise ValueError(f"Invalid category: {rule.category}")
        self._rules[(installation_id, rule.rule_id)] = rule
        return rule

    def check(self, installation_id: str, consumer_id: str, check_results: dict[str, bool], now: datetime | None = None) -> ComplianceReport:
        now = now or datetime.utcnow()
        rules = [r for (inst, _), r in self._rules.items() if inst == installation_id]
        results: list[ComplianceResult] = []
        for rule in rules:
            passed = check_results.get(rule.rule_id, False)
            results.append(ComplianceResult(rule_id=rule.rule_id, rule_name=rule.name, passed=passed, severity=rule.severity, details="Passed" if passed else "Failed"))
        passed_count = sum(1 for r in results if r.passed)
        total = len(results)
        score = (passed_count / total * 100) if total > 0 else 100.0
        report = ComplianceReport(consumer_id=consumer_id, checked_at=now, results=results, passed=passed_count, failed=total - passed_count, score=round(score, 1))
        key = (installation_id, consumer_id)
        if key not in self._reports:
            self._reports[key] = []
        self._reports[key].append(report)
        return report

    def get_latest(self, installation_id: str, consumer_id: str) -> ComplianceReport | None:
        reports = self._reports.get((installation_id, consumer_id), [])
        return reports[-1] if reports else None

    def list_rules(self, installation_id: str, category: str | None = None) -> list[ComplianceRule]:
        rules = [r for (inst, _), r in self._rules.items() if inst == installation_id]
        if category:
            rules = [r for r in rules if r.category == category]
        return rules
