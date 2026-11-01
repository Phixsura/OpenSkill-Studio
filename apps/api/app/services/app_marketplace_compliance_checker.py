"""Compliance Checker — verify extensions meet marketplace policies.

Runs pre-publish compliance checks: license validation, dependency
audit, size limits, required metadata, and prohibited patterns.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ComplianceResult:
    rule_id: str
    rule_name: str
    passed: bool
    message: str
    severity: str = "error"  # error, warning, info


APPROVED_LICENSES = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "MPL-2.0", "LGPL-3.0"}

MAX_PACKAGE_SIZE_MB = 50
MAX_DEPENDENCY_COUNT = 100
REQUIRED_METADATA = ["name", "version", "description", "author", "license"]
PROHIBITED_NAMES = {"test", "example", "demo", "untitled", "undefined"}


class ComplianceChecker:
    """Verifies extensions comply with marketplace policies."""

    def check_license(self, license_id: str) -> ComplianceResult:
        if not license_id:
            return ComplianceResult("CMP-01", "License", False, "No license specified")
        if license_id not in APPROVED_LICENSES:
            return ComplianceResult("CMP-01", "License", False,
                f"License '{license_id}' not in approved list: {', '.join(sorted(APPROVED_LICENSES))}", "warning")
        return ComplianceResult("CMP-01", "License", True, f"License {license_id} approved")

    def check_metadata(self, metadata: dict) -> list[ComplianceResult]:
        results = []
        for field_name in REQUIRED_METADATA:
            if field_name not in metadata or not metadata[field_name]:
                results.append(ComplianceResult("CMP-02", f"Metadata: {field_name}", False,
                    f"Missing required metadata: {field_name}"))
            else:
                results.append(ComplianceResult("CMP-02", f"Metadata: {field_name}", True, "Present"))
        name = metadata.get("name", "").lower()
        if name in PROHIBITED_NAMES:
            results.append(ComplianceResult("CMP-03", "Name Policy", False,
                f"Name '{name}' is prohibited"))
        return results

    def check_size(self, size_bytes: int) -> ComplianceResult:
        max_bytes = MAX_PACKAGE_SIZE_MB * 1024 * 1024
        if size_bytes > max_bytes:
            return ComplianceResult("CMP-04", "Package Size", False,
                f"Package {size_bytes / 1024 / 1024:.1f}MB exceeds {MAX_PACKAGE_SIZE_MB}MB limit")
        return ComplianceResult("CMP-04", "Package Size", True,
            f"Package {size_bytes / 1024 / 1024:.1f}MB within limits")

    def check_dependencies(self, deps: list[str]) -> ComplianceResult:
        if len(deps) > MAX_DEPENDENCY_COUNT:
            return ComplianceResult("CMP-05", "Dependencies", False,
                f"{len(deps)} dependencies exceeds limit of {MAX_DEPENDENCY_COUNT}")
        return ComplianceResult("CMP-05", "Dependencies", True,
            f"{len(deps)} dependencies within limits")

    def run_all(self, metadata: dict, size_bytes: int = 0,
                dependencies: list[str] | None = None) -> dict:
        """Run all compliance checks and return summary."""
        results: list[ComplianceResult] = []
        results.append(self.check_license(metadata.get("license", "")))
        results.extend(self.check_metadata(metadata))
        results.append(self.check_size(size_bytes))
        results.append(self.check_dependencies(dependencies or []))

        passed = all(r.passed for r in results if r.severity == "error")
        errors = [r for r in results if not r.passed and r.severity == "error"]
        warnings = [r for r in results if not r.passed and r.severity == "warning"]
        return {
            "compliant": passed,
            "total_checks": len(results),
            "passed": sum(1 for r in results if r.passed),
            "errors": [{"rule": r.rule_id, "message": r.message} for r in errors],
            "warnings": [{"rule": r.rule_id, "message": r.message} for r in warnings],
        }
