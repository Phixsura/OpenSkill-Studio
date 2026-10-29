"""Tests for App API Security Scan — findings, resolve, score."""

import pytest
from app.services.app_api_security_scan import AppAPISecurityScan


class TestFinding:
    def test_add(self):
        s = AppAPISecurityScan()
        f = s.add_finding("inst-1", "f1", "TLS Check", "high", "TLS 1.0 in use", "Upgrade to TLS 1.3")
        assert f.resolved is False

    def test_invalid_severity(self):
        s = AppAPISecurityScan()
        with pytest.raises(ValueError):
            s.add_finding("inst-1", "f1", "X", "extreme", "D")


class TestResolve:
    def test_resolve(self):
        s = AppAPISecurityScan()
        s.add_finding("inst-1", "f1", "TLS", "high", "D")
        s.resolve("inst-1", "f1")
        assert s.unresolved("inst-1") == []


class TestScore:
    def test_score(self):
        s = AppAPISecurityScan()
        s.add_finding("inst-1", "f1", "TLS", "high", "D")  # -10
        s.add_finding("inst-1", "f2", "CORS", "medium", "D")  # -5
        assert s.score("inst-1") == 85.0

    def test_perfect(self):
        s = AppAPISecurityScan()
        assert s.score("inst-1") == 100.0


class TestIsolation:
    def test_cross(self):
        s = AppAPISecurityScan()
        s.add_finding("inst-1", "f1", "X", "low", "D")
        assert s.count("inst-2") == 0
