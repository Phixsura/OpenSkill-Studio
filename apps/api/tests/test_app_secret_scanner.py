"""Tests for App Secret Scanner — pattern detection, severity, redaction."""

import pytest

from app.services.app_secret_scanner import AppSecretScanner


class TestScanConfig:
    def test_clean_config(self):
        s = AppSecretScanner()
        r = s.scan_config("inst-1", {"name": "my-app", "port": "8080"})
        assert len(r.findings) == 0
        assert r.scanned_fields == 2

    def test_detect_aws_key(self):
        s = AppSecretScanner()
        r = s.scan_config("inst-1", {"aws_access_key": "AKIAIOSFODNN7EXAMPLE"})
        assert len(r.findings) == 1
        assert r.findings[0].pattern_name == "aws_key"
        assert r.findings[0].severity == "high"

    def test_detect_github_token(self):
        s = AppSecretScanner()
        r = s.scan_config("inst-1", {"token": "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij"})
        assert r.high_count == 1

    def test_detect_password(self):
        s = AppSecretScanner()
        r = s.scan_config("inst-1", {"db_config": 'password = "super_secret_pw"'})
        assert r.medium_count >= 1

    def test_detect_private_key(self):
        s = AppSecretScanner()
        r = s.scan_config("inst-1", {"cert": "-----BEGIN PRIVATE KEY-----\nMIIE..."})
        assert r.critical_count == 1

    def test_redacted_snippet(self):
        s = AppSecretScanner()
        r = s.scan_config("inst-1", {"key": "AKIAIOSFODNN7EXAMPLE"})
        assert "AKIAIOSFODNN7EXAMPLE" not in r.findings[0].snippet
        assert "***" in r.findings[0].snippet


class TestScanText:
    def test_scan_text(self):
        s = AppSecretScanner()
        text = 'export AWS_KEY=AKIAIOSFODNN7EXAMPLE\necho "hello"'
        findings = s.scan_text("inst-1", text, location="env.sh")
        assert len(findings) >= 1
        assert findings[0].line == 1
        assert findings[0].location == "env.sh"

    def test_jwt_detection(self):
        s = AppSecretScanner()
        jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        findings = s.scan_text("inst-1", jwt)
        assert len(findings) >= 1


class TestSeverityCounts:
    def test_counts(self):
        s = AppSecretScanner()
        r = s.scan_config("inst-1", {
            "key": "AKIAIOSFODNN7EXAMPLE",
            "cert": "-----BEGIN PRIVATE KEY-----",
            "db": 'password = "mysecret123"',
        })
        assert r.critical_count >= 1
        assert r.high_count >= 1
        assert r.medium_count >= 1


class TestIsolation:
    def test_missing_installation_id(self):
        s = AppSecretScanner()
        with pytest.raises(ValueError):
            s.scan_config("", {"key": "value"})
