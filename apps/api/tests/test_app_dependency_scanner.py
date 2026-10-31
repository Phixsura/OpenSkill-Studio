"""Tests for App Dependency Scanner — vulnerabilities, scanning, findings."""

import pytest

from app.services.app_dependency_scanner import (
    AppDependencyScanner,
    Dependency,
    Severity,
    Vulnerability,
)


@pytest.fixture
def scanner():
    s = AppDependencyScanner()
    s.add_vulnerability(Vulnerability(
        vuln_id="CVE-2026-001", package="lodash", severity=Severity.CRITICAL,
        affected_versions=["4.17.20", "4.17.21"], title="Prototype pollution",
        fixed_in="4.17.22",
    ))
    s.add_vulnerability(Vulnerability(
        vuln_id="CVE-2026-002", package="express", severity=Severity.HIGH,
        affected_versions=["4.18.0"], title="Path traversal",
        fixed_in="4.18.1",
    ))
    s.add_vulnerability(Vulnerability(
        vuln_id="CVE-2026-003", package="axios", severity=Severity.MEDIUM,
        affected_versions=["1.5.0"], title="SSRF bypass",
    ))
    return s


class TestRegisterDependencies:
    def test_register(self, scanner):
        deps = [Dependency(name="lodash", version="4.17.21")]
        count = scanner.register_dependencies("inst-1", deps)
        assert count == 1

    def test_missing_installation_id(self, scanner):
        with pytest.raises(ValueError, match="installation_id"):
            scanner.register_dependencies("", [])


class TestScan:
    def test_finds_vulnerable_dep(self, scanner):
        scanner.register_dependencies("inst-1", [
            Dependency(name="lodash", version="4.17.21"),
        ])
        result = scanner.scan("inst-1")
        assert len(result.findings) == 1
        assert result.findings[0].vulnerability.vuln_id == "CVE-2026-001"
        assert result.critical_count == 1

    def test_safe_dep_no_findings(self, scanner):
        scanner.register_dependencies("inst-1", [
            Dependency(name="lodash", version="4.17.22"),
        ])
        result = scanner.scan("inst-1")
        assert len(result.findings) == 0

    def test_multiple_vulns(self, scanner):
        scanner.register_dependencies("inst-1", [
            Dependency(name="lodash", version="4.17.21"),
            Dependency(name="express", version="4.18.0"),
            Dependency(name="react", version="18.2.0"),
        ])
        result = scanner.scan("inst-1")
        assert len(result.findings) == 2
        assert result.scanned_count == 3
        assert result.critical_count == 1
        assert result.high_count == 1

    def test_fixable_finding(self, scanner):
        scanner.register_dependencies("inst-1", [
            Dependency(name="lodash", version="4.17.21"),
        ])
        result = scanner.scan("inst-1")
        assert result.findings[0].fixable is True
        assert result.findings[0].fix_version == "4.17.22"

    def test_no_fix_available(self, scanner):
        scanner.register_dependencies("inst-1", [
            Dependency(name="axios", version="1.5.0"),
        ])
        result = scanner.scan("inst-1")
        assert result.findings[0].fixable is False
        assert result.findings[0].fix_version is None

    def test_empty_deps(self, scanner):
        scanner.register_dependencies("inst-1", [])
        result = scanner.scan("inst-1")
        assert len(result.findings) == 0
        assert result.scanned_count == 0


class TestSeverityCounts:
    def test_all_severities(self, scanner):
        scanner.add_vulnerability(Vulnerability(
            vuln_id="CVE-2026-004", package="debug", severity=Severity.LOW,
            affected_versions=["4.3.0"], title="Info leak",
        ))
        scanner.register_dependencies("inst-1", [
            Dependency(name="lodash", version="4.17.21"),
            Dependency(name="express", version="4.18.0"),
            Dependency(name="axios", version="1.5.0"),
            Dependency(name="debug", version="4.3.0"),
        ])
        result = scanner.scan("inst-1")
        assert result.critical_count == 1
        assert result.high_count == 1
        assert result.medium_count == 1
        assert result.low_count == 1


class TestScanHistory:
    def test_latest_scan(self, scanner):
        scanner.register_dependencies("inst-1", [])
        scanner.scan("inst-1")
        scanner.scan("inst-1")
        latest = scanner.get_latest_scan("inst-1")
        assert latest is not None

    def test_no_scans(self, scanner):
        assert scanner.get_latest_scan("inst-1") is None

    def test_history_limit(self, scanner):
        scanner.register_dependencies("inst-1", [])
        for _ in range(5):
            scanner.scan("inst-1")
        history = scanner.get_scan_history("inst-1", limit=3)
        assert len(history) == 3


class TestIsolation:
    def test_cross_installation(self, scanner):
        scanner.register_dependencies("inst-1", [
            Dependency(name="lodash", version="4.17.21"),
        ])
        result = scanner.scan("inst-2")
        assert len(result.findings) == 0


class TestVulnDb:
    def test_missing_vuln_id(self):
        s = AppDependencyScanner()
        with pytest.raises(ValueError, match="vuln_id"):
            s.add_vulnerability(Vulnerability(
                vuln_id="", package="x", severity=Severity.LOW,
                affected_versions=[], title="x",
            ))
