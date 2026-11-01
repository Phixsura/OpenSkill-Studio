"""Tests for App Rate Limit Override — grant, check, revoke."""

import pytest

from app.services.app_rate_limit_override import AppRateLimitOverride


class TestGrant:
    def test_grant(self):
        r = AppRateLimitOverride()
        o = r.grant("inst-1", "o1", "consumer-a", 1000, "VIP customer")
        assert o.limit == 1000
        assert o.is_active is True

    def test_invalid_limit(self):
        r = AppRateLimitOverride()
        with pytest.raises(ValueError):
            r.grant("inst-1", "o1", "c", 0)


class TestLookup:
    def test_find_active(self):
        r = AppRateLimitOverride()
        r.grant("inst-1", "o1", "consumer-a", 1000)
        o = r.get_override("inst-1", "consumer-a")
        assert o is not None
        assert o.limit == 1000

    def test_no_override(self):
        r = AppRateLimitOverride()
        assert r.get_override("inst-1", "nobody") is None


class TestRevoke:
    def test_revoke(self):
        r = AppRateLimitOverride()
        r.grant("inst-1", "o1", "consumer-a", 1000)
        r.revoke("inst-1", "o1")
        assert r.get_override("inst-1", "consumer-a") is None


class TestUsage:
    def test_count(self):
        r = AppRateLimitOverride()
        r.grant("inst-1", "o1", "consumer-a", 1000)
        r.record_usage("inst-1", "o1")
        o = r.list_overrides("inst-1")[0]
        assert o.request_count == 1


class TestIsolation:
    def test_cross(self):
        r = AppRateLimitOverride()
        r.grant("inst-1", "o1", "consumer-a", 1000)
        assert r.list_overrides("inst-2") == []
