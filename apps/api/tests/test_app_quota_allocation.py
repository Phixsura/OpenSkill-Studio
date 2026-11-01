"""Tests for App Quota Allocation — consume, release, alerts."""

import pytest

from app.services.app_quota_allocation import AppQuotaAllocation


class TestSetQuota:
    def test_set(self):
        q = AppQuotaAllocation()
        quota = q.set_quota("inst-1", "api_calls", 1000, "requests")
        assert quota.limit == 1000
        assert quota.remaining == 1000

    def test_negative_limit(self):
        q = AppQuotaAllocation()
        with pytest.raises(ValueError, match="non-negative"):
            q.set_quota("inst-1", "api_calls", -1)


class TestConsume:
    def test_consume(self):
        q = AppQuotaAllocation()
        q.set_quota("inst-1", "api_calls", 100)
        quota = q.consume("inst-1", "api_calls", 30)
        assert quota.used == 30
        assert quota.remaining == 70

    def test_exceed(self):
        q = AppQuotaAllocation()
        q.set_quota("inst-1", "api_calls", 10)
        with pytest.raises(ValueError, match="exceeded"):
            q.consume("inst-1", "api_calls", 11)


class TestRelease:
    def test_release(self):
        q = AppQuotaAllocation()
        q.set_quota("inst-1", "storage", 500)
        q.consume("inst-1", "storage", 200)
        quota = q.release("inst-1", "storage", 50)
        assert quota.used == 150

    def test_release_below_zero(self):
        q = AppQuotaAllocation()
        q.set_quota("inst-1", "storage", 100)
        quota = q.release("inst-1", "storage", 50)
        assert quota.used == 0


class TestAlerts:
    def test_alerts(self):
        q = AppQuotaAllocation()
        q.set_quota("inst-1", "api_calls", 100)
        q.set_quota("inst-1", "storage", 100)
        q.consume("inst-1", "api_calls", 85)
        q.consume("inst-1", "storage", 50)
        alerts = q.alerts("inst-1", threshold_pct=80.0)
        assert len(alerts) == 1
        assert alerts[0].resource == "api_calls"


class TestReset:
    def test_reset(self):
        q = AppQuotaAllocation()
        q.set_quota("inst-1", "api_calls", 100)
        q.consume("inst-1", "api_calls", 99)
        quota = q.reset("inst-1", "api_calls")
        assert quota.used == 0


class TestIsolation:
    def test_cross(self):
        q = AppQuotaAllocation()
        q.set_quota("inst-1", "api_calls", 100)
        assert q.list_quotas("inst-2") == []
