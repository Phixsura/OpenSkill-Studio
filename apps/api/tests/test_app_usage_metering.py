"""Tests for App Usage Metering — quotas, aggregation, overage detection."""

from datetime import UTC, datetime, timedelta

import pytest

from app.services.app_usage_metering import (
    AppUsageMeter,
    MeterType,
    QuotaTier,
    UsageRecord,
    hour_key,
    day_key,
    month_key,
)


class TestTimeKeys:
    def test_hour_key_format(self):
        dt = datetime(2026, 10, 28, 14, 30, 0, tzinfo=UTC)
        assert hour_key(dt) == "2026-10-28T14"

    def test_day_key_format(self):
        dt = datetime(2026, 10, 28, 14, 30, 0, tzinfo=UTC)
        assert day_key(dt) == "2026-10-28"

    def test_month_key_format(self):
        dt = datetime(2026, 10, 28, 14, 30, 0, tzinfo=UTC)
        assert month_key(dt) == "2026-10"


class TestTierManagement:
    def test_default_tier_is_free(self):
        m = AppUsageMeter()
        assert m.get_tier("inst-1") == QuotaTier.FREE

    def test_set_and_get_tier(self):
        m = AppUsageMeter()
        m.set_tier("inst-1", QuotaTier.PROFESSIONAL)
        assert m.get_tier("inst-1") == QuotaTier.PROFESSIONAL

    def test_different_installations_independent(self):
        m = AppUsageMeter()
        m.set_tier("inst-1", QuotaTier.ENTERPRISE)
        assert m.get_tier("inst-2") == QuotaTier.FREE


class TestRecording:
    def test_record_single_request(self):
        m = AppUsageMeter()
        now = datetime(2026, 10, 28, 14, 0, 0, tzinfo=UTC)
        result = m.record(UsageRecord(
            installation_id="inst-1",
            meter_type=MeterType.API_REQUEST,
            value=1,
            endpoint="/api/v1/skills",
            method="GET",
            timestamp=now,
        ))
        assert result.allowed is True
        assert result.current_usage == 1
        assert result.remaining == 999  # free tier: 1000

    def test_accumulates_within_hour(self):
        m = AppUsageMeter()
        now = datetime(2026, 10, 28, 14, 0, 0, tzinfo=UTC)
        for i in range(50):
            m.record(UsageRecord(
                installation_id="inst-1",
                meter_type=MeterType.API_REQUEST,
                value=1,
                timestamp=now + timedelta(seconds=i),
            ))
        assert m.hourly_usage("inst-1", MeterType.API_REQUEST, now) == 50

    def test_different_hours_separate(self):
        m = AppUsageMeter()
        h1 = datetime(2026, 10, 28, 14, 0, 0, tzinfo=UTC)
        h2 = datetime(2026, 10, 28, 15, 0, 0, tzinfo=UTC)
        m.record(UsageRecord("inst-1", MeterType.API_REQUEST, 10, timestamp=h1))
        m.record(UsageRecord("inst-1", MeterType.API_REQUEST, 20, timestamp=h2))
        assert m.hourly_usage("inst-1", MeterType.API_REQUEST, h1) == 10
        assert m.hourly_usage("inst-1", MeterType.API_REQUEST, h2) == 20

    def test_bandwidth_tracking(self):
        m = AppUsageMeter()
        now = datetime(2026, 10, 28, 14, 0, 0, tzinfo=UTC)
        m.record(UsageRecord("inst-1", MeterType.BANDWIDTH_IN, 1024, timestamp=now))
        m.record(UsageRecord("inst-1", MeterType.BANDWIDTH_OUT, 4096, timestamp=now))
        assert m.hourly_usage("inst-1", MeterType.BANDWIDTH_IN, now) == 1024
        assert m.hourly_usage("inst-1", MeterType.BANDWIDTH_OUT, now) == 4096


class TestQuotaChecks:
    def test_within_quota(self):
        m = AppUsageMeter()
        now = datetime(2026, 10, 28, 14, 0, 0, tzinfo=UTC)
        result = m.check_quota("inst-1", MeterType.API_REQUEST, now)
        assert result.allowed is True
        assert result.current_usage == 0
        assert result.limit == 1_000

    def test_over_quota_blocks(self):
        m = AppUsageMeter()
        now = datetime(2026, 10, 28, 14, 0, 0, tzinfo=UTC)
        # Exceed free tier
        for _ in range(1001):
            m.record(UsageRecord("inst-1", MeterType.API_REQUEST, 1, timestamp=now))
        result = m.check_quota("inst-1", MeterType.API_REQUEST, now)
        assert result.allowed is False
        assert result.overage == 1
        assert result.usage_pct > 100

    def test_throttle_recommended_at_80pct(self):
        m = AppUsageMeter()
        now = datetime(2026, 10, 28, 14, 0, 0, tzinfo=UTC)
        for _ in range(800):
            m.record(UsageRecord("inst-1", MeterType.API_REQUEST, 1, timestamp=now))
        result = m.check_quota("inst-1", MeterType.API_REQUEST, now)
        assert result.throttle_recommended is True
        assert result.allowed is True

    def test_higher_tier_higher_limit(self):
        m = AppUsageMeter()
        m.set_tier("inst-1", QuotaTier.PROFESSIONAL)
        now = datetime(2026, 10, 28, 14, 0, 0, tzinfo=UTC)
        result = m.check_quota("inst-1", MeterType.API_REQUEST, now)
        assert result.limit == 100_000

    def test_storage_is_total_not_hourly(self):
        m = AppUsageMeter()
        h1 = datetime(2026, 10, 28, 14, 0, 0, tzinfo=UTC)
        h2 = datetime(2026, 10, 28, 15, 0, 0, tzinfo=UTC)
        m.record(UsageRecord("inst-1", MeterType.STORAGE_BYTES, 50_000_000, timestamp=h1))
        m.record(UsageRecord("inst-1", MeterType.STORAGE_BYTES, 60_000_000, timestamp=h2))
        result = m.check_quota("inst-1", MeterType.STORAGE_BYTES, h2)
        # Total = 110MB, free limit = 100MB → over
        assert result.current_usage == 110_000_000
        assert result.allowed is False


class TestAggregation:
    def test_daily_usage(self):
        m = AppUsageMeter()
        base = datetime(2026, 10, 28, 0, 0, 0, tzinfo=UTC)
        for h in range(24):
            m.record(UsageRecord(
                "inst-1", MeterType.API_REQUEST, 10,
                timestamp=base + timedelta(hours=h),
            ))
        assert m.daily_usage("inst-1", MeterType.API_REQUEST, base) == 240

    def test_monthly_usage(self):
        m = AppUsageMeter()
        base = datetime(2026, 10, 1, 12, 0, 0, tzinfo=UTC)
        for d in range(5):
            m.record(UsageRecord(
                "inst-1", MeterType.API_REQUEST, 100,
                timestamp=base + timedelta(days=d),
            ))
        assert m.monthly_usage("inst-1", MeterType.API_REQUEST, base) == 500

    def test_daily_excludes_other_days(self):
        m = AppUsageMeter()
        d1 = datetime(2026, 10, 27, 12, 0, 0, tzinfo=UTC)
        d2 = datetime(2026, 10, 28, 12, 0, 0, tzinfo=UTC)
        m.record(UsageRecord("inst-1", MeterType.API_REQUEST, 50, timestamp=d1))
        m.record(UsageRecord("inst-1", MeterType.API_REQUEST, 75, timestamp=d2))
        assert m.daily_usage("inst-1", MeterType.API_REQUEST, d2) == 75


class TestTopEndpoints:
    def test_returns_sorted_by_count(self):
        m = AppUsageMeter()
        now = datetime(2026, 10, 28, 14, 0, 0, tzinfo=UTC)
        for _ in range(10):
            m.record(UsageRecord("inst-1", MeterType.API_REQUEST, 1,
                                 endpoint="/api/v1/skills", method="GET", timestamp=now))
        for _ in range(25):
            m.record(UsageRecord("inst-1", MeterType.API_REQUEST, 1,
                                 endpoint="/api/v1/projects", method="POST", timestamp=now))
        top = m.top_endpoints("inst-1", now, limit=5)
        assert len(top) == 2
        assert top[0]["endpoint"] == "/api/v1/projects"
        assert top[0]["count"] == 25
        assert top[1]["endpoint"] == "/api/v1/skills"

    def test_respects_limit(self):
        m = AppUsageMeter()
        now = datetime(2026, 10, 28, 14, 0, 0, tzinfo=UTC)
        for i in range(20):
            m.record(UsageRecord("inst-1", MeterType.API_REQUEST, 1,
                                 endpoint=f"/api/v1/ep{i}", method="GET", timestamp=now))
        top = m.top_endpoints("inst-1", now, limit=5)
        assert len(top) == 5

    def test_empty_when_no_data(self):
        m = AppUsageMeter()
        now = datetime(2026, 10, 28, 14, 0, 0, tzinfo=UTC)
        assert m.top_endpoints("inst-1", now) == []


class TestUsageReport:
    def test_report_structure(self):
        m = AppUsageMeter()
        now = datetime(2026, 10, 28, 14, 0, 0, tzinfo=UTC)
        m.record(UsageRecord("inst-1", MeterType.API_REQUEST, 5, timestamp=now))

        report = m.usage_report("inst-1", now)
        assert report["installation_id"] == "inst-1"
        assert report["tier"] == "free"
        assert "meters" in report
        assert "api_request" in report["meters"]

        api = report["meters"]["api_request"]
        assert api["current_hour"] == 5
        assert api["today"] == 5
        assert api["limit_per_hour"] == 1000
        assert api["allowed"] is True

    def test_report_covers_all_meter_types(self):
        m = AppUsageMeter()
        now = datetime(2026, 10, 28, 14, 0, 0, tzinfo=UTC)
        report = m.usage_report("inst-1", now)
        for mt in MeterType:
            assert mt.value in report["meters"]
