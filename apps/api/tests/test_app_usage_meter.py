"""Tests for App Usage Meter — recording, aggregation, quotas."""

import time

import pytest

from app.services.app_usage_meter import AppUsageMeter, TimeWindow


# Fixed timestamps for 2026-10-28 10:30:00 UTC
TS = 1793168400.0  # approx


class TestRecord:
    def test_record_event(self):
        m = AppUsageMeter()
        e = m.record("inst-1", "api_calls", 1.0, now=TS)
        assert e.metric == "api_calls"
        assert e.quantity == 1.0

    def test_record_custom_quantity(self):
        m = AppUsageMeter()
        e = m.record("inst-1", "storage_bytes", 1024.0, now=TS)
        assert e.quantity == 1024.0

    def test_missing_installation_id(self):
        m = AppUsageMeter()
        with pytest.raises(ValueError, match="installation_id"):
            m.record("", "api_calls")

    def test_missing_metric(self):
        m = AppUsageMeter()
        with pytest.raises(ValueError, match="metric"):
            m.record("inst-1", "")

    def test_negative_quantity(self):
        m = AppUsageMeter()
        with pytest.raises(ValueError, match="positive"):
            m.record("inst-1", "api_calls", -1)


class TestAggregation:
    def test_hourly_aggregation(self):
        m = AppUsageMeter()
        m.record("inst-1", "api_calls", 5, now=TS)
        m.record("inst-1", "api_calls", 3, now=TS + 60)
        s = m.get_usage("inst-1", "api_calls", TimeWindow.HOURLY, now=TS)
        assert s.total == 8
        assert s.count == 2

    def test_daily_aggregation(self):
        m = AppUsageMeter()
        m.record("inst-1", "api_calls", 10, now=TS)
        m.record("inst-1", "api_calls", 20, now=TS + 3600)
        s = m.get_usage("inst-1", "api_calls", TimeWindow.DAILY, now=TS)
        assert s.total == 30

    def test_different_windows_isolated(self):
        m = AppUsageMeter()
        m.record("inst-1", "api_calls", 5, now=TS)
        m.record("inst-1", "api_calls", 5, now=TS + 86400)  # next day
        s = m.get_usage("inst-1", "api_calls", TimeWindow.DAILY, now=TS)
        assert s.total == 5  # only first day

    def test_empty_metric(self):
        m = AppUsageMeter()
        s = m.get_usage("inst-1", "api_calls", TimeWindow.DAILY, now=TS)
        assert s.total == 0
        assert s.count == 0


class TestQuota:
    def test_set_quota(self):
        m = AppUsageMeter()
        q = m.set_quota("inst-1", "api_calls", 1000, TimeWindow.DAILY)
        assert q.limit == 1000

    def test_invalid_limit(self):
        m = AppUsageMeter()
        with pytest.raises(ValueError, match="positive"):
            m.set_quota("inst-1", "api_calls", 0, TimeWindow.DAILY)

    def test_check_quota_under(self):
        m = AppUsageMeter()
        m.set_quota("inst-1", "api_calls", 100, TimeWindow.DAILY)
        m.record("inst-1", "api_calls", 30, now=TS)
        s = m.check_quota("inst-1", "api_calls", now=TS)
        assert s.exceeded is False
        assert s.remaining == 70
        assert s.usage_pct == 30.0

    def test_check_quota_exceeded(self):
        m = AppUsageMeter()
        m.set_quota("inst-1", "api_calls", 10, TimeWindow.DAILY)
        m.record("inst-1", "api_calls", 15, now=TS)
        s = m.check_quota("inst-1", "api_calls", now=TS)
        assert s.exceeded is True
        assert s.remaining == 0
        assert s.usage_pct == 100.0

    def test_no_quota_raises(self):
        m = AppUsageMeter()
        with pytest.raises(KeyError):
            m.check_quota("inst-1", "api_calls")


class TestCanConsume:
    def test_within_quota(self):
        m = AppUsageMeter()
        m.set_quota("inst-1", "api_calls", 100, TimeWindow.DAILY)
        m.record("inst-1", "api_calls", 50, now=TS)
        assert m.can_consume("inst-1", "api_calls", 50, now=TS) is True

    def test_over_quota(self):
        m = AppUsageMeter()
        m.set_quota("inst-1", "api_calls", 100, TimeWindow.DAILY)
        m.record("inst-1", "api_calls", 90, now=TS)
        assert m.can_consume("inst-1", "api_calls", 20, now=TS) is False

    def test_no_quota_allows(self):
        m = AppUsageMeter()
        assert m.can_consume("inst-1", "api_calls", 999999) is True


class TestMetrics:
    def test_list_metrics(self):
        m = AppUsageMeter()
        m.record("inst-1", "api_calls", 1, now=TS)
        m.record("inst-1", "storage_bytes", 100, now=TS)
        metrics = m.list_metrics("inst-1")
        assert set(metrics) == {"api_calls", "storage_bytes"}

    def test_get_total(self):
        m = AppUsageMeter()
        m.record("inst-1", "api_calls", 10, now=TS)
        m.record("inst-1", "api_calls", 20, now=TS + 86400)
        assert m.get_total("inst-1", "api_calls") == 30


class TestIsolation:
    def test_different_installations(self):
        m = AppUsageMeter()
        m.record("inst-1", "api_calls", 100, now=TS)
        s = m.get_usage("inst-2", "api_calls", TimeWindow.DAILY, now=TS)
        assert s.total == 0
