from app.services.app_marketplace_security_scanner import (
    SecurityScanner, Severity,
)


def test_clean_code():
    scanner = SecurityScanner()
    safe, findings = scanner.is_safe("def hello():\n    return 'world'")
    assert safe is True


def test_detect_eval():
    scanner = SecurityScanner()
    findings = scanner.scan("result = eval(user_input)")
    assert any(f.rule_id == "SEC001" for f in findings)
    assert any("eval" in f.message for f in findings)


def test_detect_hardcoded_secret():
    scanner = SecurityScanner()
    code = 'api_key = "sk_test_FAKE_NOT_REAL_KEY_FOR_TESTING"'
    findings = scanner.scan(code)
    critical = [f for f in findings if f.severity == Severity.CRITICAL]
    assert len(critical) >= 1


def test_detect_dangerous_import():
    scanner = SecurityScanner()
    findings = scanner.scan("import subprocess\nsubprocess.run(['rm', '-rf', '/'])")
    assert any("subprocess" in f.message for f in findings)


def test_is_safe_blocks_critical():
    scanner = SecurityScanner()
    safe, findings = scanner.is_safe('password = "super_secret_password_12345"')
    assert safe is False


def test_scan_summary():
    scanner = SecurityScanner()
    code = "import os\neval('x')\ndef safe(): pass"
    summary = scanner.scan_summary(code)
    assert summary["total_findings"] >= 1
    assert isinstance(summary["by_severity"], dict)


def test_custom_rules():
    scanner = SecurityScanner(custom_rules=[
        (r"print\(", "No print statements in production", Severity.LOW),
    ])
    findings = scanner.scan("print('debug')")
    assert any(f.rule_id == "CUSTOM" for f in findings)
