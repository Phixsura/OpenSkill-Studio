"""Tests for App DNS Resolver — lookup, cache, expiry, failures."""

import pytest

from app.services.app_dns_resolver import AppDNSResolver


class TestRecordLookup:
    def test_record(self):
        r = AppDNSResolver()
        rec = r.record_lookup("inst-1", "api.example.com", ["10.0.0.1", "10.0.0.2"], ttl_seconds=300, now=1000.0)
        assert rec.hostname == "api.example.com"
        assert len(rec.addresses) == 2

    def test_missing_hostname(self):
        r = AppDNSResolver()
        with pytest.raises(ValueError):
            r.record_lookup("inst-1", "", [])


class TestResolve:
    def test_cached(self):
        r = AppDNSResolver()
        r.record_lookup("inst-1", "api.example.com", ["10.0.0.1"], ttl_seconds=300, now=1000.0)
        rec = r.resolve("inst-1", "api.example.com", now=1100.0)
        assert rec is not None
        assert rec.addresses == ["10.0.0.1"]

    def test_expired(self):
        r = AppDNSResolver()
        r.record_lookup("inst-1", "api.example.com", ["10.0.0.1"], ttl_seconds=60, now=1000.0)
        rec = r.resolve("inst-1", "api.example.com", now=1061.0)
        assert rec is None

    def test_miss(self):
        r = AppDNSResolver()
        assert r.resolve("inst-1", "nope.com") is None


class TestFailure:
    def test_record_failure(self):
        r = AppDNSResolver()
        rec = r.record_failure("inst-1", "bad.example.com", error="NXDOMAIN")
        assert rec.failed is True
        assert rec.error == "NXDOMAIN"

    def test_failed_lookups(self):
        r = AppDNSResolver()
        r.record_lookup("inst-1", "good.com", ["1.2.3.4"])
        r.record_failure("inst-1", "bad.com", "timeout")
        failed = r.failed_lookups("inst-1")
        assert len(failed) == 1


class TestIsCached:
    def test_cached(self):
        r = AppDNSResolver()
        r.record_lookup("inst-1", "api.com", ["1.2.3.4"], now=1000.0)
        assert r.is_cached("inst-1", "api.com", now=1000.0) is True

    def test_not_cached(self):
        r = AppDNSResolver()
        assert r.is_cached("inst-1", "nope.com") is False


class TestIsolation:
    def test_cross_installation(self):
        r = AppDNSResolver()
        r.record_lookup("inst-1", "api.com", ["1.2.3.4"])
        assert r.resolve("inst-2", "api.com") is None
