"""Tests for App API Header Policy — require, forbid, default."""

import pytest

from app.services.app_api_header_policy import AppAPIHeaderPolicy


class TestRequire:
    def test_present(self):
        p = AppAPIHeaderPolicy()
        p.add_rule("inst-1", "r1", "X-Request-Id", "require")
        result = p.apply_policy("inst-1", {"X-Request-Id": "abc"})
        assert result["violations"] == []

    def test_missing(self):
        p = AppAPIHeaderPolicy()
        p.add_rule("inst-1", "r1", "X-Request-Id", "require")
        result = p.apply_policy("inst-1", {})
        assert len(result["violations"]) == 1


class TestForbid:
    def test_strip(self):
        p = AppAPIHeaderPolicy()
        p.add_rule("inst-1", "r1", "Server", "forbid")
        result = p.apply_policy("inst-1", {"Server": "nginx", "Content-Type": "json"})
        assert "Server" not in result["headers"]
        assert "Content-Type" in result["headers"]


class TestDefault:
    def test_set_default(self):
        p = AppAPIHeaderPolicy()
        p.add_rule("inst-1", "r1", "X-Frame-Options", "set_default", "DENY")
        result = p.apply_policy("inst-1", {})
        assert result["headers"]["X-Frame-Options"] == "DENY"

    def test_no_overwrite(self):
        p = AppAPIHeaderPolicy()
        p.add_rule("inst-1", "r1", "X-Frame-Options", "set_default", "DENY")
        result = p.apply_policy("inst-1", {"X-Frame-Options": "SAMEORIGIN"})
        assert result["headers"]["X-Frame-Options"] == "SAMEORIGIN"


class TestIsolation:
    def test_cross(self):
        p = AppAPIHeaderPolicy()
        p.add_rule("inst-1", "r1", "Server", "forbid")
        result = p.apply_policy("inst-2", {"Server": "nginx"})
        assert "Server" in result["headers"]
