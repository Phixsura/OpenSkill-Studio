"""App API Developer Platform Audit Compliance — track audit readiness across frameworks."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class AuditFramework:
    framework: str
    total_controls: int
    compliant: int = 0
    non_compliant: int = 0
    not_assessed: int = 0

    @property
    def compliance_pct(self) -> float:
        assessed = self.compliant + self.non_compliant
        return round(self.compliant / assessed * 100, 1) if assessed > 0 else 0.0

    @property
    def assessment_pct(self) -> float:
        return round((self.compliant + self.non_compliant) / self.total_controls * 100, 1) if self.total_controls > 0 else 0.0

    @property
    def audit_ready(self) -> bool:
        return self.compliance_pct >= 95 and self.assessment_pct >= 90

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformAuditCompliance:
    def __init__(self) -> None:
        self._frameworks: dict[tuple[str, str], AuditFramework] = {}

    def add_framework(self, installation_id: str, framework: str, total_controls: int, compliant: int = 0, non_compliant: int = 0) -> AuditFramework:
        if not installation_id: raise ValueError("installation_id is required")
        if total_controls < 1: raise ValueError("total_controls must be >= 1")
        not_assessed = total_controls - compliant - non_compliant
        f = AuditFramework(framework=framework, total_controls=total_controls, compliant=compliant, non_compliant=non_compliant, not_assessed=not_assessed)
        self._frameworks[(installation_id, framework)] = f
        return f

    def audit_ready_frameworks(self, installation_id: str) -> list[AuditFramework]:
        return [f for (inst, _), f in self._frameworks.items() if inst == installation_id and f.audit_ready]

    def overall_compliance(self, installation_id: str) -> float:
        frameworks = [f for (inst, _), f in self._frameworks.items() if inst == installation_id]
        if not frameworks: return 0.0
        total_compliant = sum(f.compliant for f in frameworks)
        total_assessed = sum(f.compliant + f.non_compliant for f in frameworks)
        return round(total_compliant / total_assessed * 100, 1) if total_assessed > 0 else 0.0

    def all_frameworks(self, installation_id: str) -> list[AuditFramework]:
        return [f for (inst, _), f in self._frameworks.items() if inst == installation_id]
