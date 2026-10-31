from app.services.app_marketplace_secret_scanner import SecretScanner


def test_clean_code():
    scanner = SecretScanner()
    safe, findings = scanner.scan_safe("def hello():\n    return 'world'")
    assert safe is True
    assert findings == []


def test_detect_api_key():
    scanner = SecretScanner()
    code = 'api_key = "abcdef1234567890abcdef"'
    findings = scanner.scan(code)
    assert len(findings) >= 1
    assert findings[0].rule_id == "SEC-S01"


def test_detect_password():
    scanner = SecretScanner()
    code = 'password = "super_secret_pass_123"'
    findings = scanner.scan(code)
    assert any(f.rule_id == "SEC-S02" for f in findings)


def test_detect_private_key():
    scanner = SecretScanner()
    code = '-----BEGIN PRIVATE KEY-----\nMIIE...'
    findings = scanner.scan(code)
    assert any(f.rule_id == "SEC-S04" for f in findings)


def test_allowlist_skips_examples():
    scanner = SecretScanner()
    code = 'api_key = "your_api_key_placeholder_here"'
    findings = scanner.scan(code)
    assert len(findings) == 0  # "your_" is allowlisted


def test_allowlist_localhost():
    scanner = SecretScanner()
    code = 'db_url = "postgres://user:pass@localhost:5432/db"'
    findings = scanner.scan(code)
    assert len(findings) == 0  # localhost is allowlisted


def test_redaction():
    scanner = SecretScanner()
    code = 'token = "abcdefghijklmnopqrstuvwxyz1234567890"'
    findings = scanner.scan(code)
    assert len(findings) >= 1
    assert "***" in findings[0].redacted_match


def test_list_rules():
    scanner = SecretScanner()
    rules = scanner.get_rules()
    assert len(rules) >= 7
    assert all("id" in r and "description" in r for r in rules)
