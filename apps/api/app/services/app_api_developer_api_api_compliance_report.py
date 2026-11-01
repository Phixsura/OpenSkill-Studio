"""App API Developer API Compliance Report — track regulatory compliance status."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ComplianceCheck:
    check_id: str
    framework: str  # "SOC2", "GDPR", "HIPAA", "PCI_DSS", "ISO27001"
    requirement: str
    status: str = "pending"  # "pending", "compliant", "non_compliant", "not_applicable"
    evidence: str = ""

class AppAPIDeveloperAPIApiComplianceReport:
    def __init__(self) -> None:
        self._checks: dict[tuple[str, str], ComplianceCheck] = {}

    def add_check(self, installation_id: str, check_id: str, framework: str, requirement: str) -> ComplianceCheck:
        if not installation_id: raise ValueError("installation_id is required")
        valid_frameworks = {"SOC2", "GDPR", "HIPAA", "PCI_DSS", "ISO27001"}
        if framework not in valid_frameworks: raise ValueError(f"Unknown framework: {framework}")
        key = (installation_id, check_id)
        if key in self._checks: raise ValueError(f"Check {check_id} exists")
        c = ComplianceCheck(check_id=check_id, framework=framework, requirement=requirement)
        self._checks[key] = c
        return c

    def update_status(self, installation_id: str, check_id: str, status: str, evidence: str = "") -> ComplianceCheck:
        valid = {"pending", "compliant", "non_compliant", "not_applicable"}
        if status not in valid: raise ValueError(f"Invalid status: {status}")
        c = self._get(installation_id, check_id)
        c.status = status
        c.evidence = evidence
        return c

    def compliance_rate(self, installation_id: str, framework: str | None = None) -> float:
        checks = [c for (inst, _), c in self._checks.items() if inst == installation_id]
        if framework: checks = [c for c in checks if c.framework == framework]
        applicable = [c for c in checks if c.status != "not_applicable"]
        if not applicable: return 100.0
        compliant = sum(1 for c in applicable if c.status == "compliant")
        return round(compliant / len(applicable) * 100, 1)

    def non_compliant(self, installation_id: str) -> list[ComplianceCheck]:
        return [c for (inst, _), c in self._checks.items() if inst == installation_id and c.status == "non_compliant"]

    def by_framework(self, installation_id: str) -> dict[str, dict[str, int]]:
        result: dict[str, dict[str, int]] = {}
        for (inst, _), c in self._checks.items():
            if inst != installation_id: continue
            fw = result.setdefault(c.framework, {"compliant": 0, "non_compliant": 0, "pending": 0})
            if c.status in fw: fw[c.status] += 1
        return result

    def _get(self, installation_id: str, check_id: str) -> ComplianceCheck:
        key = (installation_id, check_id)
        c = self._checks.get(key)
        if c is None: raise KeyError(f"Check {check_id} not found")
        return c
