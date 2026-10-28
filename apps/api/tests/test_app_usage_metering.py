"""Tests for App Usage Metering — record, aggregate, summary."""

import pytest

from app.services.app_usage_metering import AppUsageMetering


class TestRecord:
    def test_record(self):
        m = AppUsageMetering()
        total = m.record("inst-1", "api_calls", 10, "2024-01-15")
        assert total == 10

    def test_accumulate(self):
        m = AppUsageMetering()
        m.record("inst-1", "api_calls", 10, "2024-01-15")
        total = m.record("inst-1", "api_calls", 5, "2024-01-15")
        assert total == 15

    def test_negative(self):
        m = AppUsageMetering()
        with pytest.raises(ValueError):
            m.record("inst-1", "api_calls", -1, "2024-01-15")


class TestAggregate:
    def test_metric_total(self):
        m = AppUsageMetering()
        m.record("inst-1", "api_calls", 10, "2024-01-15")
        m.record("inst-1", "api_calls", 20, "2024-01-16")
        assert m.get_metric_total("inst-1", "api_calls") == 30

    def test_periods(self):
        m = AppUsageMetering()
        m.record("inst-1", "api_calls", 10, "2024-01-15")
        m.record("inst-1", "api_calls", 20, "2024-01-16")
        periods = m.get_periods("inst-1", "api_calls")
        assert len(periods) == 2
        assert periods[0]["period"] == "2024-01-15"


class TestSummary:
    def test_summary(self):
        m = AppUsageMetering()
        m.record("inst-1", "api_calls", 100, "2024-01-15")
        m.record("inst-1", "storage_mb", 50, "2024-01-15")
        summary = m.summary("inst-1")
        assert len(summary) == 2
        names = [s["metric"] for s in summary]
        assert "api_calls" in names


class TestIsolation:
    def test_cross(self):
        m = AppUsageMetering()
        m.record("inst-1", "api_calls", 10, "2024-01-15")
        assert m.list_metrics("inst-2") == []
