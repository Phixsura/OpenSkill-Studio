"""Tests for App API Usage Quota — set, increment, overage."""

import pytest

from app.services.app_api_usage_quota import AppAPIUsageQuota


class TestSet:
    def test_set(self):
        q = AppAPIUsageQuota()
        uq = q.set_quota("inst-1", "api_calls", 10000, "2024-01")
        assert uq.remaining == 10000


class TestIncrement:
    def test_increment(self):
        q = AppAPIUsageQuota()
        q.set_quota("inst-1", "api_calls", 100, "2024-01")
        uq = q.increment("inst-1", "api_calls", "2024-01", 50)
        assert uq.used == 50
        assert uq.usage_pct == 50.0


class TestOverage:
    def test_over(self):
        q = AppAPIUsageQuota()
        q.set_quota("inst-1", "api_calls", 10, "2024-01")
        q.increment("inst-1", "api_calls", "2024-01", 15)
        overages = q.overages("inst-1", "2024-01")
        assert len(overages) == 1
        assert overages[0].is_over is True

    def test_no_overage(self):
        q = AppAPIUsageQuota()
        q.set_quota("inst-1", "api_calls", 100, "2024-01")
        q.increment("inst-1", "api_calls", "2024-01", 50)
        assert q.overages("inst-1", "2024-01") == []


class TestSummary:
    def test_summary(self):
        q = AppAPIUsageQuota()
        q.set_quota("inst-1", "api_calls", 1000, "2024-01")
        q.set_quota("inst-1", "storage", 500, "2024-01")
        q.increment("inst-1", "api_calls", "2024-01", 800)
        s = q.summary("inst-1", "2024-01")
        assert len(s) == 2


class TestIsolation:
    def test_cross(self):
        q = AppAPIUsageQuota()
        q.set_quota("inst-1", "api_calls", 100, "2024-01")
        assert q.summary("inst-2", "2024-01") == []
