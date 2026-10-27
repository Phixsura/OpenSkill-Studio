"""Tests for App Analytics Aggregator — counting, summaries, time series, top-N."""

from datetime import UTC, datetime, timedelta

import pytest

from app.services.app_analytics_aggregator import (
    AppAnalyticsAggregator,
    MetricEvent,
    MetricType,
    Period,
)


class TestRecording:
    def test_record_increments_counter(self):
        a = AppAnalyticsAggregator()
        now = datetime.now(UTC)
        a.record(MetricEvent("app-1", MetricType.API_CALL, timestamp=now))
        a.record(MetricEvent("app-1", MetricType.API_CALL, timestamp=now))
        assert a.get_count("app-1", MetricType.API_CALL, Period.DAY, now) == 2

    def test_record_batch(self):
        a = AppAnalyticsAggregator()
        now = datetime.now(UTC)
        events = [MetricEvent("app-1", MetricType.INSTALL, timestamp=now) for _ in range(5)]
        count = a.record_batch(events)
        assert count == 5
        assert a.get_count("app-1", MetricType.INSTALL, Period.DAY, now) == 5

    def test_different_apps_independent(self):
        a = AppAnalyticsAggregator()
        now = datetime.now(UTC)
        a.record(MetricEvent("app-1", MetricType.API_CALL, timestamp=now))
        a.record(MetricEvent("app-2", MetricType.API_CALL, timestamp=now))
        assert a.get_count("app-1", MetricType.API_CALL, Period.DAY, now) == 1
        assert a.get_count("app-2", MetricType.API_CALL, Period.DAY, now) == 1

    def test_active_users_tracked(self):
        a = AppAnalyticsAggregator()
        now = datetime.now(UTC)
        a.record(MetricEvent("app-1", MetricType.ACTIVE_USER, user_id="u1", timestamp=now))
        a.record(MetricEvent("app-1", MetricType.ACTIVE_USER, user_id="u2", timestamp=now))
        a.record(MetricEvent("app-1", MetricType.ACTIVE_USER, user_id="u1", timestamp=now))  # dup
        assert a.get_active_users("app-1", Period.DAY, now) == 2


class TestSummary:
    def test_summary_all_metrics(self):
        a = AppAnalyticsAggregator()
        now = datetime.now(UTC)
        for _ in range(10):
            a.record(MetricEvent("app-1", MetricType.INSTALL, timestamp=now))
        for _ in range(3):
            a.record(MetricEvent("app-1", MetricType.UNINSTALL, timestamp=now))
        for _ in range(100):
            a.record(MetricEvent("app-1", MetricType.API_CALL, timestamp=now))
        for _ in range(5):
            a.record(MetricEvent("app-1", MetricType.ERROR, timestamp=now))

        s = a.get_summary("app-1", Period.DAY, now)
        assert s.total_installs == 10
        assert s.total_uninstalls == 3
        assert s.total_api_calls == 100
        assert s.total_errors == 5
        assert s.net_installs == 7
        assert s.error_rate == 5.0
        assert s.growth_rate == 70.0

    def test_summary_zero_division(self):
        a = AppAnalyticsAggregator()
        s = a.get_summary("app-x", Period.DAY)
        assert s.error_rate == 0.0
        assert s.growth_rate == 0.0
        assert s.net_installs == 0


class TestTimeSeries:
    def test_daily_series(self):
        a = AppAnalyticsAggregator()
        base = datetime(2026, 10, 25, 12, 0, 0, tzinfo=UTC)
        for day_offset in range(5):
            dt = base + timedelta(days=day_offset)
            for _ in range(day_offset + 1):
                a.record(MetricEvent("app-1", MetricType.API_CALL, timestamp=dt))

        series = a.get_time_series("app-1", MetricType.API_CALL, Period.DAY,
                                    periods=5, end_dt=base + timedelta(days=4))
        assert len(series) == 5
        values = [p.value for p in series]
        assert values == [1, 2, 3, 4, 5]

    def test_empty_periods_zero(self):
        a = AppAnalyticsAggregator()
        now = datetime.now(UTC)
        series = a.get_time_series("app-1", MetricType.INSTALL, Period.DAY,
                                    periods=3, end_dt=now)
        assert all(p.value == 0 for p in series)


class TestTopApps:
    def test_top_by_installs(self):
        a = AppAnalyticsAggregator()
        now = datetime.now(UTC)
        for _ in range(50):
            a.record(MetricEvent("popular", MetricType.INSTALL, timestamp=now))
        for _ in range(20):
            a.record(MetricEvent("medium", MetricType.INSTALL, timestamp=now))
        for _ in range(5):
            a.record(MetricEvent("niche", MetricType.INSTALL, timestamp=now))

        top = a.top_apps(MetricType.INSTALL, Period.DAY, limit=3, dt=now)
        assert len(top) == 3
        assert top[0].app_id == "popular"
        assert top[0].rank == 1
        assert top[1].app_id == "medium"
        assert top[2].app_id == "niche"

    def test_top_limit(self):
        a = AppAnalyticsAggregator()
        now = datetime.now(UTC)
        for i in range(10):
            a.record(MetricEvent(f"app-{i}", MetricType.API_CALL, timestamp=now))
        top = a.top_apps(MetricType.API_CALL, Period.DAY, limit=3, dt=now)
        assert len(top) == 3

    def test_top_empty(self):
        a = AppAnalyticsAggregator()
        top = a.top_apps(MetricType.INSTALL, Period.DAY)
        assert top == []


class TestPeriods:
    def test_weekly_aggregation(self):
        a = AppAnalyticsAggregator()
        now = datetime.now(UTC)
        a.record(MetricEvent("app-1", MetricType.API_CALL, timestamp=now))
        assert a.get_count("app-1", MetricType.API_CALL, Period.WEEK, now) == 1

    def test_monthly_aggregation(self):
        a = AppAnalyticsAggregator()
        now = datetime.now(UTC)
        a.record(MetricEvent("app-1", MetricType.API_CALL, timestamp=now))
        assert a.get_count("app-1", MetricType.API_CALL, Period.MONTH, now) == 1

    def test_different_days_same_month(self):
        a = AppAnalyticsAggregator()
        d1 = datetime(2026, 10, 1, tzinfo=UTC)
        d2 = datetime(2026, 10, 28, tzinfo=UTC)
        a.record(MetricEvent("app-1", MetricType.INSTALL, timestamp=d1))
        a.record(MetricEvent("app-1", MetricType.INSTALL, timestamp=d2))
        assert a.get_count("app-1", MetricType.INSTALL, Period.MONTH, d1) == 2
