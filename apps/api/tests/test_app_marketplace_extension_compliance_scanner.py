from app.services.app_marketplace_extension_compliance_scanner import (
    ExtensionComplianceScannerService, ComplianceLevel,
)


def test_all_pass():
    svc = ExtensionComplianceScannerService()
    report = svc.scan("ext-1", {
        "manifest.json": '{}', "README.md": "# Readme", "LICENSE": "MIT License",
    })
    assert report.passed is True
    assert report.score >= 90


def test_missing_files():
    svc = ExtensionComplianceScannerService()
    report = svc.scan("ext-1", {"manifest.json": "{}"})
    assert report.passed is False
    assert any(c.message == "Missing README.md" for c in report.checks)


def test_forbidden_pattern():
    svc = ExtensionComplianceScannerService()
    report = svc.scan("ext-1", {
        "manifest.json": '{}', "README.md": "#", "LICENSE": "MIT",
        "code.js": 'eval("dangerous")',
    })
    assert any(c.level == ComplianceLevel.FAIL and "eval" in c.message for c in report.checks)


def test_network_requires_privacy():
    svc = ExtensionComplianceScannerService()
    report = svc.scan("ext-1", {"manifest.json": '{}', "README.md": "#", "LICENSE": "MIT"},
                      manifest={"permissions": ["network:outbound"]})
    assert any(c.name == "network_privacy" for c in report.checks)


def test_copyleft_warning():
    svc = ExtensionComplianceScannerService()
    report = svc.scan("ext-1", {
        "manifest.json": '{}', "README.md": "#", "LICENSE": "GNU GPL v3",
    })
    assert any(c.level == ComplianceLevel.WARN and "Copyleft" in c.message for c in report.checks)


def test_score_calculation():
    svc = ExtensionComplianceScannerService()
    report = svc.scan("ext-1", {"manifest.json": "{}"})  # missing README + LICENSE
    assert report.score < 100
