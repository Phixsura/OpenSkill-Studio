"""Tests for App API Key Usage — record, top keys, endpoints."""

import pytest

from app.services.app_api_key_usage import AppAPIKeyUsage


class TestRecord:
    def test_record(self):
        u = AppAPIKeyUsage()
        r = u.record("inst-1", "k1", "/api/users", True)
        assert r.total_requests == 1

    def test_accumulate(self):
        u = AppAPIKeyUsage()
        u.record("inst-1", "k1", "/api/users", True)
        u.record("inst-1", "k1", "/api/users", False)
        r = u.get_usage("inst-1", "k1")
        assert r.total_requests == 2
        assert r.error_rate == 50.0


class TestTopKeys:
    def test_ranked(self):
        u = AppAPIKeyUsage()
        for _ in range(10):
            u.record("inst-1", "k1", "/api", True)
        for _ in range(5):
            u.record("inst-1", "k2", "/api", True)
        top = u.top_keys("inst-1")
        assert top[0].key_id == "k1"


class TestEndpoints:
    def test_top_endpoints(self):
        u = AppAPIKeyUsage()
        for _ in range(5):
            u.record("inst-1", "k1", "/api/users", True)
        for _ in range(3):
            u.record("inst-1", "k1", "/api/apps", True)
        eps = u.top_endpoints("inst-1", "k1")
        assert eps[0]["endpoint"] == "/api/users"


class TestIsolation:
    def test_cross(self):
        u = AppAPIKeyUsage()
        u.record("inst-1", "k1", "/api", True)
        assert u.top_keys("inst-2") == []
