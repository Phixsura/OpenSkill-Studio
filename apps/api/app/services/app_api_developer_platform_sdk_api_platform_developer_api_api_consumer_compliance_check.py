"""API Consumer Compliance Check — verify consumer compliance with API policies."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import structlog

log = structlog.get_logger()

class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"

@dataclass
class ComplianceRule:
    rule_id: str
    name: str
    description: str = ""
    severity: str = "medium"  # "low", "medium", "high", "critical"
    auto_check: bool = True

@dataclass
class ComplianceResult:
    consumer_id: str
    rule_id: str
    status: ComplianceStatus
    details: str = ""

VALID_SEVERITIES = {"low", "medium", "high", "critical"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerComplianceCheck:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], ComplianceRule] = {}
        self._results: dict[tuple[str, str, str], ComplianceResult] = {}

    def add_rule(self, installation_id: str, rule: ComplianceRule) -> ComplianceRule:
        if not installation_id: raise ValueError("installation_id is required")
        if rule.severity not in VALID_SEVERITIES: raise ValueError(f"Invalid severity: {rule.severity}")
        self._rules[(installation_id, rule.rule_id)] = rule
        return rule

    def record_result(self, installation_id: str, consumer_id: str, rule_id: str, status: ComplianceStatus, details: str = "") -> ComplianceResult:
        if (installation_id, rule_id) not in self._rules: raise KeyError(f"Rule {rule_id} not found")
        result = ComplianceResult(consumer_id=consumer_id, rule_id=rule_id, status=status, details=details)
        self._results[(installation_id, consumer_id, rule_id)] = result
        return result

    def check_consumer(self, installation_id: str, consumer_id: str) -> dict[str, object]:
        rules = [r for (inst, _), r in self._rules.items() if inst == installation_id]
        results = [r for (inst, cid, _), r in self._results.items() if inst == installation_id and cid == consumer_id]
        compliant = sum(1 for r in results if r.status == ComplianceStatus.COMPLIANT)
        non_compliant = sum(1 for r in results if r.status == ComplianceStatus.NON_COMPLIANT)
        return {"total_rules": len(rules), "checked": len(results), "compliant": compliant, "non_compliant": non_compliant, "overall": "compliant" if non_compliant == 0 and len(results) == len(rules) else "non_compliant"}

    def non_compliant_consumers(self, installation_id: str) -> list[str]:
        consumers: set[str] = set()
        for (inst, cid, _), r in self._results.items():
            if inst == installation_id and r.status == ComplianceStatus.NON_COMPLIANT:
                consumers.add(cid)
        return list(consumers)

    def list_rules(self, installation_id: str) -> list[ComplianceRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id]
