"""Compliance Scanner — scan extensions for policy and security compliance.

Checks for required files, license compliance, API usage patterns,
data handling declarations, and generates compliance reports.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class ComplianceLevel(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass
class ComplianceCheck:
    name: str
    level: ComplianceLevel
    message: str
    category: str  # security, privacy, licensing, quality


@dataclass
class ComplianceReport:
    extension_id: str
    checks: list[ComplianceCheck] = field(default_factory=list)
    score: int = 100
    passed: bool = True


REQUIRED_FILES = ["manifest.json", "README.md", "LICENSE"]
FORBIDDEN_PATTERNS = ["eval(", "exec(", "document.write(", "__import__"]


class ExtensionComplianceScannerService:
    """Scans extensions for compliance with marketplace policies."""

    def scan(self, extension_id: str, files: dict[str, str],
             manifest: dict | None = None) -> ComplianceReport:
        checks: list[ComplianceCheck] = []

        # Required files
        for req in REQUIRED_FILES:
            if req in files:
                checks.append(ComplianceCheck(req, ComplianceLevel.PASS,
                                              f"{req} present", "quality"))
            else:
                checks.append(ComplianceCheck(req, ComplianceLevel.FAIL,
                                              f"Missing {req}", "quality"))

        # License check
        license_content = files.get("LICENSE", "")
        if license_content:
            if any(k in license_content.upper() for k in ["MIT", "APACHE", "BSD"]):
                checks.append(ComplianceCheck("license_type", ComplianceLevel.PASS,
                                              "Permissive license", "licensing"))
            elif "GPL" in license_content.upper():
                checks.append(ComplianceCheck("license_type", ComplianceLevel.WARN,
                                              "Copyleft license — review required", "licensing"))

        # Security patterns
        for filename, content in files.items():
            for pattern in FORBIDDEN_PATTERNS:
                if pattern in content:
                    checks.append(ComplianceCheck(
                        f"forbidden_{pattern[:8]}", ComplianceLevel.FAIL,
                        f"Forbidden pattern '{pattern}' in {filename}", "security"))

        # Manifest checks
        if manifest:
            if "privacy_policy" not in manifest and "privacy_url" not in manifest:
                checks.append(ComplianceCheck("privacy", ComplianceLevel.WARN,
                                              "No privacy policy declared", "privacy"))
            perms = manifest.get("permissions", [])
            if "network:outbound" in perms and "privacy_policy" not in manifest:
                checks.append(ComplianceCheck("network_privacy", ComplianceLevel.FAIL,
                                              "Network access requires privacy policy", "privacy"))

        # Calculate score
        fails = sum(1 for c in checks if c.level == ComplianceLevel.FAIL)
        warns = sum(1 for c in checks if c.level == ComplianceLevel.WARN)
        score = max(0, 100 - fails * 20 - warns * 5)

        return ComplianceReport(
            extension_id=extension_id, checks=checks,
            score=score, passed=fails == 0,
        )
