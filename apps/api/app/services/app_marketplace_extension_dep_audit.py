"""Dependency Audit — security and license audit for extension dependencies.

Scans dependency trees for known vulnerabilities, license conflicts,
outdated packages, and generates compliance reports.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class VulnSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LicenseRisk(str, Enum):
    PERMISSIVE = "permissive"    # MIT, Apache-2.0, BSD
    WEAK_COPYLEFT = "weak_copyleft"  # LGPL, MPL
    STRONG_COPYLEFT = "strong_copyleft"  # GPL, AGPL
    UNKNOWN = "unknown"


LICENSE_RISK_MAP: dict[str, LicenseRisk] = {
    "MIT": LicenseRisk.PERMISSIVE, "Apache-2.0": LicenseRisk.PERMISSIVE,
    "BSD-2-Clause": LicenseRisk.PERMISSIVE, "BSD-3-Clause": LicenseRisk.PERMISSIVE,
    "ISC": LicenseRisk.PERMISSIVE,
    "LGPL-2.1": LicenseRisk.WEAK_COPYLEFT, "LGPL-3.0": LicenseRisk.WEAK_COPYLEFT,
    "MPL-2.0": LicenseRisk.WEAK_COPYLEFT,
    "GPL-2.0": LicenseRisk.STRONG_COPYLEFT, "GPL-3.0": LicenseRisk.STRONG_COPYLEFT,
    "AGPL-3.0": LicenseRisk.STRONG_COPYLEFT,
}


@dataclass
class Vulnerability:
    vuln_id: str
    package: str
    severity: VulnSeverity
    title: str
    fixed_in: str = ""
    url: str = ""


@dataclass
class DependencyInfo:
    name: str
    version: str
    license: str
    license_risk: LicenseRisk = LicenseRisk.UNKNOWN
    is_outdated: bool = False
    latest_version: str = ""
    vulnerabilities: list[Vulnerability] = field(default_factory=list)


@dataclass
class AuditReport:
    extension_id: str
    total_deps: int
    vulns_critical: int = 0
    vulns_high: int = 0
    vulns_medium: int = 0
    vulns_low: int = 0
    license_issues: int = 0
    outdated: int = 0
    passed: bool = True
    details: list[DependencyInfo] = field(default_factory=list)


class DepAuditService:
    """Audits extension dependencies for security and compliance."""

    def __init__(self):
        self._vuln_db: dict[str, list[Vulnerability]] = {}
        self._blocked_licenses: set[str] = {"GPL-3.0", "AGPL-3.0"}

    def register_vulnerability(self, package: str, vuln_id: str,
                               severity: VulnSeverity, title: str,
                               fixed_in: str = "") -> None:
        self._vuln_db.setdefault(package, []).append(
            Vulnerability(vuln_id=vuln_id, package=package,
                          severity=severity, title=title, fixed_in=fixed_in))

    def audit(self, extension_id: str,
              dependencies: list[dict]) -> AuditReport:
        report = AuditReport(extension_id=extension_id, total_deps=len(dependencies))
        
        for dep in dependencies:
            name = dep["name"]
            version = dep["version"]
            license_id = dep.get("license", "Unknown")
            latest = dep.get("latest_version", version)

            risk = LICENSE_RISK_MAP.get(license_id, LicenseRisk.UNKNOWN)
            is_outdated = version != latest

            vulns = self._vuln_db.get(name, [])
            active_vulns = [v for v in vulns
                            if not v.fixed_in or v.fixed_in > version]

            info = DependencyInfo(
                name=name, version=version, license=license_id,
                license_risk=risk, is_outdated=is_outdated,
                latest_version=latest, vulnerabilities=active_vulns,
            )
            report.details.append(info)

            for v in active_vulns:
                if v.severity == VulnSeverity.CRITICAL:
                    report.vulns_critical += 1
                elif v.severity == VulnSeverity.HIGH:
                    report.vulns_high += 1
                elif v.severity == VulnSeverity.MEDIUM:
                    report.vulns_medium += 1
                else:
                    report.vulns_low += 1

            if license_id in self._blocked_licenses:
                report.license_issues += 1

            if is_outdated:
                report.outdated += 1

        report.passed = (report.vulns_critical == 0
                         and report.vulns_high == 0
                         and report.license_issues == 0)
        return report

    def set_blocked_licenses(self, licenses: set[str]) -> None:
        self._blocked_licenses = licenses
