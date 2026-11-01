"""App API Security Scan — run security scans on API configurations.

Manages security scans:
- Define security checks
- Run scans and track findings
- Severity classification
- Per-installation scoped scans
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class SecurityFinding:
    """A security scan finding."""

    finding_id: str
    check_name: str
    severity: str  # "info", "low", "medium", "high", "critical"
    description: str
    remediation: str = ""
    resolved: bool = False


class AppAPISecurityScan:
    """Run security scans on API configurations."""

    def __init__(self) -> None:
        self._findings: dict[str, list[SecurityFinding]] = {}

    def add_finding(
        self, installation_id: str, finding_id: str, check_name: str,
        severity: str, description: str, remediation: str = "",
    ) -> SecurityFinding:
        if not installation_id:
            raise ValueError("installation_id is required")
        if severity not in ("info", "low", "medium", "high", "critical"):
            raise ValueError("invalid severity")

        finding = SecurityFinding(
            finding_id=finding_id, check_name=check_name,
            severity=severity, description=description, remediation=remediation,
        )
        self._findings.setdefault(installation_id, []).append(finding)
        return finding

    def resolve(self, installation_id: str, finding_id: str) -> SecurityFinding:
        for f in self._findings.get(installation_id, []):
            if f.finding_id == finding_id:
                f.resolved = True
                return f
        raise KeyError(f"Finding {finding_id} not found")

    def unresolved(self, installation_id: str) -> list[SecurityFinding]:
        return [f for f in self._findings.get(installation_id, []) if not f.resolved]

    def by_severity(self, installation_id: str, severity: str) -> list[SecurityFinding]:
        return [f for f in self._findings.get(installation_id, []) if f.severity == severity]

    def score(self, installation_id: str) -> float:
        """Security score: 100 - (weighted unresolved findings)."""
        weights = {"info": 1, "low": 2, "medium": 5, "high": 10, "critical": 25}
        unresolved = self.unresolved(installation_id)
        penalty = sum(weights.get(f.severity, 1) for f in unresolved)
        return max(0.0, round(100 - penalty, 1))

    def count(self, installation_id: str) -> int:
        return len(self._findings.get(installation_id, []))
