"""Tests for App Secret Scanner — scan, detect, resolve."""

import pytest

from app.services.app_secret_scanner import AppSecretScanner


class TestScan:
    def test_detect_aws_key(self):
        s = AppSecretScanner()
        text = "config: AKIAIOSFODNN7EXAMPLE"
        findings = s.scan("inst-1", text, "config.yaml")
        assert len(findings) == 1
        assert findings[0].pattern_name == "aws_key"

    def test_detect_github_token(self):
        s = AppSecretScanner()
        text = "token = ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijkl"
        findings = s.scan("inst-1", text, ".env")
        names = [f.pattern_name for f in findings]
        assert "github_token" in names

    def test_detect_private_key(self):
        s = AppSecretScanner()
        text = "-----BEGIN RSA PRIVATE KEY-----\nMIIE..."
        findings = s.scan("inst-1", text, "id_rsa")
        assert any(f.severity == "critical" for f in findings)

    def test_detect_connection_string(self):
        s = AppSecretScanner()
        text = 'DB_URL = "postgres://user:pass@host:5432/db"'
        findings = s.scan("inst-1", text, ".env")
        names = [f.pattern_name for f in findings]
        assert "connection_string" in names

    def test_no_findings(self):
        s = AppSecretScanner()
        findings = s.scan("inst-1", "Hello world", "readme.md")
        assert findings == []

    def test_redacted(self):
        s = AppSecretScanner()
        findings = s.scan("inst-1", "AKIAIOSFODNN7EXAMPLE", "file")
        assert "..." in findings[0].matched_text


class TestResolve:
    def test_resolve(self):
        s = AppSecretScanner()
        findings = s.scan("inst-1", "AKIAIOSFODNN7EXAMPLE", "file")
        f = s.resolve("inst-1", findings[0].finding_id)
        assert f.resolved is True
        assert s.unresolved("inst-1") == []


class TestIsolation:
    def test_cross(self):
        s = AppSecretScanner()
        s.scan("inst-1", "AKIAIOSFODNN7EXAMPLE", "file")
        assert s.count("inst-2") == 0
