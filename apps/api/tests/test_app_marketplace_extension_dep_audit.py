from app.services.app_marketplace_extension_dep_audit import (
    DepAuditService, VulnSeverity, LicenseRisk,
)


def test_clean_audit():
    svc = DepAuditService()
    report = svc.audit("ext-1", [
        {"name": "lodash", "version": "4.17.21", "license": "MIT"},
    ])
    assert report.passed is True
    assert report.total_deps == 1
    assert report.vulns_critical == 0


def test_vulnerability_detected():
    svc = DepAuditService()
    svc.register_vulnerability("lodash", "CVE-2021-23337", VulnSeverity.HIGH,
                               "Prototype Pollution", fixed_in="4.17.21")
    report = svc.audit("ext-1", [
        {"name": "lodash", "version": "4.17.20", "license": "MIT"},
    ])
    assert report.passed is False
    assert report.vulns_high == 1


def test_fixed_vuln_not_counted():
    svc = DepAuditService()
    svc.register_vulnerability("pkg", "CVE-1", VulnSeverity.CRITICAL,
                               "Bug", fixed_in="1.0.0")
    report = svc.audit("ext-1", [
        {"name": "pkg", "version": "2.0.0", "license": "MIT"},
    ])
    assert report.vulns_critical == 0
    assert report.passed is True


def test_license_block():
    svc = DepAuditService()
    report = svc.audit("ext-1", [
        {"name": "gpl-lib", "version": "1.0.0", "license": "GPL-3.0"},
    ])
    assert report.passed is False
    assert report.license_issues == 1


def test_license_risk_classification():
    svc = DepAuditService()
    report = svc.audit("ext-1", [
        {"name": "a", "version": "1.0", "license": "MIT"},
        {"name": "b", "version": "1.0", "license": "LGPL-3.0"},
    ])
    assert report.details[0].license_risk == LicenseRisk.PERMISSIVE
    assert report.details[1].license_risk == LicenseRisk.WEAK_COPYLEFT


def test_outdated_detection():
    svc = DepAuditService()
    report = svc.audit("ext-1", [
        {"name": "pkg", "version": "1.0.0", "license": "MIT", "latest_version": "2.0.0"},
    ])
    assert report.outdated == 1
    assert report.details[0].is_outdated is True


def test_multiple_vulns():
    svc = DepAuditService()
    svc.register_vulnerability("bad-pkg", "CVE-1", VulnSeverity.CRITICAL, "RCE")
    svc.register_vulnerability("bad-pkg", "CVE-2", VulnSeverity.MEDIUM, "XSS")
    report = svc.audit("ext-1", [
        {"name": "bad-pkg", "version": "0.1.0", "license": "MIT"},
    ])
    assert report.vulns_critical == 1
    assert report.vulns_medium == 1
