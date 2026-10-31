"""Tests for App CORS Policy — origins, preflight, credentials."""

import pytest

from app.services.app_cors_policy import AppCORSPolicy


class TestSetPolicy:
    def test_set(self):
        c = AppCORSPolicy()
        p = c.set_policy("inst-1", "p1", ["https://app.example.com"])
        assert p.allowed_origins == ["https://app.example.com"]

    def test_credentials_wildcard(self):
        c = AppCORSPolicy()
        with pytest.raises(ValueError, match="wildcard"):
            c.set_policy("inst-1", "p1", ["*"], allow_credentials=True)


class TestCheckOrigin:
    def test_allowed(self):
        c = AppCORSPolicy()
        c.set_policy("inst-1", "p1", ["https://app.example.com"])
        assert c.check_origin("inst-1", "https://app.example.com") is not None

    def test_denied(self):
        c = AppCORSPolicy()
        c.set_policy("inst-1", "p1", ["https://app.example.com"])
        assert c.check_origin("inst-1", "https://evil.com") is None

    def test_wildcard(self):
        c = AppCORSPolicy()
        c.set_policy("inst-1", "p1", ["*"])
        assert c.check_origin("inst-1", "https://anything.com") is not None


class TestPreflight:
    def test_allowed(self):
        c = AppCORSPolicy()
        c.set_policy("inst-1", "p1", ["https://app.example.com"])
        result = c.evaluate_preflight("inst-1", "https://app.example.com", "POST")
        assert result["allowed"] is True

    def test_method_denied(self):
        c = AppCORSPolicy()
        c.set_policy("inst-1", "p1", ["*"], allowed_methods=["GET"])
        result = c.evaluate_preflight("inst-1", "https://app.com", "DELETE")
        assert result["allowed"] is False

    def test_header_denied(self):
        c = AppCORSPolicy()
        c.set_policy("inst-1", "p1", ["*"], allowed_headers=["Content-Type"])
        result = c.evaluate_preflight("inst-1", "https://app.com", "GET", ["X-Custom"])
        assert result["allowed"] is False


class TestIsolation:
    def test_cross(self):
        c = AppCORSPolicy()
        c.set_policy("inst-1", "p1", ["https://app.com"])
        assert c.check_origin("inst-2", "https://app.com") is None
