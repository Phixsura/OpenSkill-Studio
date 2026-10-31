"""App Dependency Scanner — scan app dependencies for vulnerabilities.

Scans declared dependencies of installed apps:
- Register dependencies with version info
- Check against known vulnerability database (in-memory)
- Severity levels: critical, high, medium, low
- Per-installation scoped scans
- Summary statistics
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Dependency:
    """A declared dependency."""

    name: str
    version: str
    ecosystem: str = "npm"  # npm, pypi, maven, etc.


@dataclass
class Vulnerability:
    """A known vulnerability."""

    vuln_id: str
    package: str
    affected_versions: list[str]  # simplified: list of exact versions
    severity: Severity
    title: str
    fixed_in: str | None = None


@dataclass
class ScanFinding:
    """A finding from scanning a dependency."""

    dependency: Dependency
    vulnerability: Vulnerability
    fixable: bool = False
    fix_version: str | None = None


@dataclass
class ScanResult:
    """Result of scanning all dependencies."""

    installation_id: str
    findings: list[ScanFinding]
    scanned_count: int
    timestamp: float = field(default_factory=time.time)
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0


class AppDependencyScanner:
    """Scan app dependencies for known vulnerabilities."""

    def __init__(self) -> None:
        # Known vulnerability database
        self._vulns: list[Vulnerability] = []
        # (installation_id) → list[Dependency]
        self._deps: dict[str, list[Dependency]] = {}
        # Scan history
        self._scans: dict[str, list[ScanResult]] = {}

    def add_vulnerability(self, vuln: Vulnerability) -> None:
        """Add a known vulnerability to the database."""
        if not vuln.vuln_id:
            raise ValueError("vuln_id is required")
        self._vulns.append(vuln)

    def register_dependencies(
        self, installation_id: str, deps: list[Dependency]
    ) -> int:
        """Register dependencies for an installation. Returns count."""
        if not installation_id:
            raise ValueError("installation_id is required")
        self._deps[installation_id] = list(deps)
        return len(deps)

    def scan(self, installation_id: str) -> ScanResult:
        """Scan dependencies for vulnerabilities."""
        if not installation_id:
            raise ValueError("installation_id is required")

        deps = self._deps.get(installation_id, [])
        findings: list[ScanFinding] = []

        for dep in deps:
            for vuln in self._vulns:
                if dep.name == vuln.package and dep.version in vuln.affected_versions:
                    finding = ScanFinding(
                        dependency=dep,
                        vulnerability=vuln,
                        fixable=vuln.fixed_in is not None,
                        fix_version=vuln.fixed_in,
                    )
                    findings.append(finding)

        counts = {s: 0 for s in Severity}
        for f in findings:
            counts[f.vulnerability.severity] += 1

        result = ScanResult(
            installation_id=installation_id,
            findings=findings,
            scanned_count=len(deps),
            critical_count=counts[Severity.CRITICAL],
            high_count=counts[Severity.HIGH],
            medium_count=counts[Severity.MEDIUM],
            low_count=counts[Severity.LOW],
        )

        self._scans.setdefault(installation_id, []).append(result)
        log.info("dependency_scan.completed",
                 installation_id=installation_id,
                 findings=len(findings), scanned=len(deps))
        return result

    def get_latest_scan(self, installation_id: str) -> ScanResult | None:
        """Get the most recent scan result."""
        scans = self._scans.get(installation_id, [])
        return scans[-1] if scans else None

    def get_dependencies(self, installation_id: str) -> list[Dependency]:
        return list(self._deps.get(installation_id, []))

    def get_scan_history(self, installation_id: str, limit: int = 10) -> list[ScanResult]:
        scans = self._scans.get(installation_id, [])
        return list(reversed(scans[-limit:]))
