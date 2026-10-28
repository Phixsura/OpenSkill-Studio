"""Tests for App Cache Policy — rules, lookup, hit/miss tracking."""

import pytest

from app.services.app_cache_policy import AppCachePolicy


class TestAddRule:
    def test_add(self):
        c = AppCachePolicy()
        r = c.add_rule("inst-1", "r1", "/api/v1/users/*", 300)
        assert r.ttl_seconds == 300
        assert r.methods == ["GET"]


class TestLookup:
    def test_exact_match(self):
        c = AppCachePolicy()
        c.add_rule("inst-1", "r1", "/api/v1/health", 60)
        r = c.lookup("inst-1", "GET", "/api/v1/health")
        assert r is not None

    def test_wildcard_match(self):
        c = AppCachePolicy()
        c.add_rule("inst-1", "r1", "/api/v1/users/*", 300)
        r = c.lookup("inst-1", "GET", "/api/v1/users/123")
        assert r is not None

    def test_method_filter(self):
        c = AppCachePolicy()
        c.add_rule("inst-1", "r1", "/api/v1/users/*", 300, methods=["GET"])
        assert c.lookup("inst-1", "POST", "/api/v1/users/123") is None

    def test_disabled(self):
        c = AppCachePolicy()
        c.add_rule("inst-1", "r1", "/api/v1/health", 60)
        c.toggle("inst-1", "r1", False)
        assert c.lookup("inst-1", "GET", "/api/v1/health") is None


class TestHitMiss:
    def test_tracking(self):
        c = AppCachePolicy()
        c.add_rule("inst-1", "r1", "/api/*", 300)
        c.record_hit("inst-1", "r1")
        c.record_hit("inst-1", "r1")
        c.record_miss("inst-1", "r1")
        r = c.list_rules("inst-1")[0]
        assert r.hit_rate == 66.7


class TestIsolation:
    def test_cross(self):
        c = AppCachePolicy()
        c.add_rule("inst-1", "r1", "/*", 300)
        assert c.list_rules("inst-2") == []
