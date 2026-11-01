"""Tests for App Usage Forecast — trends, predictions, days to limit."""

import pytest

from app.services.app_usage_forecast import AppUsageForecast


class TestRecord:
    def test_record(self):
        f = AppUsageForecast()
        f.record("inst-1", "api_calls", 100, 1000.0)
        f.record("inst-1", "api_calls", 200, 2000.0)

    def test_missing_metric(self):
        f = AppUsageForecast()
        with pytest.raises(ValueError):
            f.record("inst-1", "", 100, 1000.0)


class TestForecast:
    def test_growing_trend(self):
        f = AppUsageForecast()
        # 100 per day growth
        for day in range(10):
            ts = day * 86400.0
            f.record("inst-1", "api_calls", 100 + day * 100, ts)
        result = f.forecast("inst-1", "api_calls", 10 * 86400.0)
        assert result.trend == "growing"
        assert result.growth_rate_per_day > 0

    def test_declining_trend(self):
        f = AppUsageForecast()
        for day in range(10):
            ts = day * 86400.0
            f.record("inst-1", "errors", 1000 - day * 100, ts)
        result = f.forecast("inst-1", "errors", 10 * 86400.0)
        assert result.trend == "declining"

    def test_stable_trend(self):
        f = AppUsageForecast()
        for day in range(10):
            ts = day * 86400.0
            f.record("inst-1", "x", 100, ts)  # constant
        result = f.forecast("inst-1", "x", 10 * 86400.0)
        assert result.trend == "stable"

    def test_too_few_points(self):
        f = AppUsageForecast()
        f.record("inst-1", "x", 100, 1000.0)
        with pytest.raises(ValueError, match="2 data points"):
            f.forecast("inst-1", "x", 2000.0)


class TestDaysToLimit:
    def test_days_computed(self):
        f = AppUsageForecast()
        for day in range(5):
            ts = day * 86400.0
            f.record("inst-1", "storage", 100 + day * 10, ts)
        result = f.forecast("inst-1", "storage", 5 * 86400.0, limit=200)
        assert result.days_to_limit is not None
        assert result.days_to_limit > 0

    def test_no_limit(self):
        f = AppUsageForecast()
        for day in range(5):
            f.record("inst-1", "x", day * 10, day * 86400.0)
        result = f.forecast("inst-1", "x", 5 * 86400.0)
        assert result.days_to_limit is None

    def test_declining_no_exhaust(self):
        f = AppUsageForecast()
        for day in range(5):
            f.record("inst-1", "x", 100 - day * 10, day * 86400.0)
        result = f.forecast("inst-1", "x", 5 * 86400.0, limit=200)
        assert result.days_to_limit is None


class TestIsolation:
    def test_cross_installation(self):
        f = AppUsageForecast()
        for day in range(5):
            f.record("inst-1", "x", day * 10, day * 86400.0)
        with pytest.raises(ValueError):
            f.forecast("inst-2", "x", 5 * 86400.0)
