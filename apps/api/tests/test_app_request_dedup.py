"""Tests for App Request Dedup — hash, TTL, cleanup, stats."""

import pytest

from app.services.app_request_dedup import AppRequestDedup


class TestCheck:
    def test_first_not_duplicate(self):
        d = AppRequestDedup()
        r = d.check("inst-1", "POST", "/api/orders", '{"item":"a"}', now=1000.0)
        assert r.is_duplicate is False

    def test_same_is_duplicate(self):
        d = AppRequestDedup()
        d.check("inst-1", "POST", "/api/orders", '{"item":"a"}', now=1000.0)
        r = d.check("inst-1", "POST", "/api/orders", '{"item":"a"}', now=1001.0)
        assert r.is_duplicate is True
        assert r.duplicate_count == 1

    def test_different_not_duplicate(self):
        d = AppRequestDedup()
        d.check("inst-1", "POST", "/api/orders", '{"item":"a"}', now=1000.0)
        r = d.check("inst-1", "POST", "/api/orders", '{"item":"b"}', now=1001.0)
        assert r.is_duplicate is False

    def test_different_method_not_duplicate(self):
        d = AppRequestDedup()
        d.check("inst-1", "GET", "/api/orders", "", now=1000.0)
        r = d.check("inst-1", "POST", "/api/orders", "", now=1001.0)
        assert r.is_duplicate is False


class TestTTL:
    def test_expired_not_duplicate(self):
        d = AppRequestDedup(ttl_seconds=60)
        d.check("inst-1", "POST", "/api", "body", now=1000.0)
        r = d.check("inst-1", "POST", "/api", "body", now=1061.0)
        assert r.is_duplicate is False

    def test_within_ttl_is_duplicate(self):
        d = AppRequestDedup(ttl_seconds=60)
        d.check("inst-1", "POST", "/api", "body", now=1000.0)
        r = d.check("inst-1", "POST", "/api", "body", now=1050.0)
        assert r.is_duplicate is True


class TestCleanup:
    def test_cleanup(self):
        d = AppRequestDedup(ttl_seconds=10)
        d.check("inst-1", "GET", "/a", "", now=1000.0)
        d.check("inst-1", "GET", "/b", "", now=1000.0)
        count = d.cleanup_expired(now=1011.0)
        assert count == 2


class TestStats:
    def test_stats(self):
        d = AppRequestDedup()
        d.check("inst-1", "POST", "/api", "a", now=1000.0)
        d.check("inst-1", "POST", "/api", "a", now=1001.0)
        s = d.stats("inst-1")
        assert s["tracked"] == 1
        assert s["total_duplicates"] == 1


class TestIsolation:
    def test_cross_installation(self):
        d = AppRequestDedup()
        d.check("inst-1", "POST", "/api", "body", now=1000.0)
        r = d.check("inst-2", "POST", "/api", "body", now=1001.0)
        assert r.is_duplicate is False


class TestConfig:
    def test_invalid_ttl(self):
        with pytest.raises(ValueError):
            AppRequestDedup(ttl_seconds=0)
