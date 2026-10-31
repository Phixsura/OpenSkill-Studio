"""App Compliance Audit — track compliance audit events and findings.

Manages compliance audit trails:
- Record audit events with severity
- Track remediation status
- Generate compliance score
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class AuditFinding:
    """A compliance audit finding."""

    finding_id: str
    category: str  # "data_privacy", "security", "access_control"
    severity: str  # "critical", "high", "medium", "low"
    description: str
    remediated: bool = False
    remediated_at: float | None = None
    found_at: float = field(default_factory=time.time)


class AppComplianceAudit:
    """Track compliance audit events and findings."""

    def __init__(self) -> None:
        self._findings: dict[tuple[str, str], AuditFinding] = {}

    def add_finding(
        self,
        installation_id: str,
        finding_id: str,
        category: str,
        severity: str,
        description: str,
        now: float | None = None,
    ) -> AuditFinding:
        if not installation_id:
            raise ValueError("installation_id is required")
        if severity not in ("critical", "high", "medium", "low"):
            raise ValueError("Invalid severity")

        key = (installation_id, finding_id)
        finding = AuditFinding(
            finding_id=finding_id, category=category,
            severity=severity, description=description,
            found_at=now or time.time(),
        )
        self._findings[key] = finding
        return finding

    def remediate(
        self, installation_id: str, finding_id: str, now: float | None = None
    ) -> AuditFinding:
        f = self._get(installation_id, finding_id)
        f.remediated = True
        f.remediated_at = now or time.time()
        return f

    def compliance_score(self, installation_id: str) -> float:
        """Score 0-100 based on remediation of findings."""
        findings = [f for (inst, _), f in self._findings.items() if inst == installation_id]
        if not findings:
            return 100.0
        remediated = sum(1 for f in findings if f.remediated)
        return round(remediated / len(findings) * 100, 1)

    def list_findings(
        self, installation_id: str, open_only: bool = False
    ) -> list[AuditFinding]:
        findings = [f for (inst, _), f in self._findings.items() if inst == installation_id]
        if open_only:
            findings = [f for f in findings if not f.remediated]
        return findings

    def severity_counts(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), f in self._findings.items():
            if inst == installation_id and not f.remediated:
                counts[f.severity] = counts.get(f.severity, 0) + 1
        return counts

    def _get(self, installation_id: str, finding_id: str) -> AuditFinding:
        key = (installation_id, finding_id)
        f = self._findings.get(key)
        if f is None:
            raise KeyError(f"Finding {finding_id} not found")
        return f
