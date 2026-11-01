"""Tests for API Deprecation Tracker — lifecycle, headers, enforcement, reporting."""

from datetime import UTC, datetime, timedelta

import pytest

from app.services.api_deprecation_tracker import (
    ApiDeprecationTracker,
    DeprecationPhase,
    EnforcementAction,
)


class TestDeprecation:
    def test_deprecate_creates_notice(self):
        t = ApiDeprecationTracker()
        sunset = datetime.now(UTC) + timedelta(days=90)
        notice = t.deprecate("GET /api/v1/old", sunset_at=sunset, replacement="/api/v2/new")
        assert notice.endpoint_key == "GET /api/v1/old"
        assert notice.phase == DeprecationPhase.DEPRECATED
        assert notice.replacement == "/api/v2/new"

    def test_list_notices(self):
        t = ApiDeprecationTracker()
        t.deprecate("GET /a", sunset_at=datetime.now(UTC) + timedelta(days=30))
        t.deprecate("GET /b", sunset_at=datetime.now(UTC) + timedelta(days=60))
        notices = t.list_notices()
        assert len(notices) == 2
        assert notices[0].endpoint_key == "GET /a"  # earlier sunset first


class TestCheckEndpoint:
    def test_non_deprecated_allowed(self):
        t = ApiDeprecationTracker()
        result = t.check("GET /api/v1/active", "client-1")
        assert result.action == EnforcementAction.ALLOW
        assert result.notice is None

    def test_deprecated_warns_with_headers(self):
        t = ApiDeprecationTracker()
        sunset = datetime.now(UTC) + timedelta(days=30)
        t.deprecate("GET /api/v1/old", sunset_at=sunset, replacement="/api/v2/new")
        result = t.check("GET /api/v1/old", "client-1")
        assert result.action == EnforcementAction.WARN
        assert "Deprecation" in result.headers
        assert "Sunset" in result.headers
        assert "successor-version" in result.headers.get("Link", "")

    def test_sunset_blocks(self):
        t = ApiDeprecationTracker()
        sunset = datetime.now(UTC) - timedelta(days=1)  # already past
        t.deprecate("GET /api/v1/old", sunset_at=sunset)
        result = t.check("GET /api/v1/old", "client-1")
        assert result.action == EnforcementAction.BLOCK

    def test_sunset_no_block_when_disabled(self):
        t = ApiDeprecationTracker()
        sunset = datetime.now(UTC) - timedelta(days=1)
        t.deprecate("GET /api/v1/old", sunset_at=sunset, block_after_sunset=False)
        result = t.check("GET /api/v1/old", "client-1")
        assert result.action == EnforcementAction.WARN  # warn only, no block

    def test_removed_always_blocks(self):
        t = ApiDeprecationTracker()
        sunset = datetime.now(UTC) + timedelta(days=30)
        t.deprecate("GET /api/v1/old", sunset_at=sunset)
        t.remove("GET /api/v1/old")
        result = t.check("GET /api/v1/old", "client-1")
        assert result.action == EnforcementAction.BLOCK

    def test_sunset_header_format(self):
        t = ApiDeprecationTracker()
        sunset = datetime(2027, 1, 15, 12, 0, 0, tzinfo=UTC)
        t.deprecate("GET /api/v1/old", sunset_at=sunset)
        result = t.check("GET /api/v1/old", "client-1",
                          now=datetime(2026, 12, 1, tzinfo=UTC))
        assert "Jan" in result.headers["Sunset"] or "15" in result.headers["Sunset"]


class TestUsageTracking:
    def test_tracks_call_count(self):
        t = ApiDeprecationTracker()
        sunset = datetime.now(UTC) + timedelta(days=30)
        t.deprecate("GET /api/v1/old", sunset_at=sunset)
        for _ in range(5):
            t.check("GET /api/v1/old", "client-1")
        consumers = t.get_consumers("GET /api/v1/old")
        assert len(consumers) == 1
        assert consumers[0].call_count == 5
        assert consumers[0].client_id == "client-1"

    def test_tracks_multiple_clients(self):
        t = ApiDeprecationTracker()
        sunset = datetime.now(UTC) + timedelta(days=30)
        t.deprecate("GET /api/v1/old", sunset_at=sunset)
        for _ in range(3):
            t.check("GET /api/v1/old", "client-1")
        t.check("GET /api/v1/old", "client-2")
        assert t.get_consumer_count("GET /api/v1/old") == 2

    def test_consumers_sorted_by_count(self):
        t = ApiDeprecationTracker()
        sunset = datetime.now(UTC) + timedelta(days=30)
        t.deprecate("GET /api/v1/old", sunset_at=sunset)
        t.check("GET /api/v1/old", "low-user")
        for _ in range(10):
            t.check("GET /api/v1/old", "heavy-user")
        consumers = t.get_consumers("GET /api/v1/old")
        assert consumers[0].client_id == "heavy-user"

    def test_warned_flag_set(self):
        t = ApiDeprecationTracker()
        sunset = datetime.now(UTC) + timedelta(days=30)
        t.deprecate("GET /api/v1/old", sunset_at=sunset)
        t.check("GET /api/v1/old", "client-1")
        consumers = t.get_consumers("GET /api/v1/old")
        assert consumers[0].warned is True


class TestReport:
    def test_report_structure(self):
        t = ApiDeprecationTracker()
        now = datetime.now(UTC)
        t.deprecate("GET /a", sunset_at=now + timedelta(days=30))
        t.deprecate("GET /b", sunset_at=now - timedelta(days=1))  # sunset
        t.check("GET /a", "c1")
        t.check("GET /b", "c2", now=now)

        report = t.get_report(now=now)
        assert report.total_deprecated >= 1
        assert report.total_sunset >= 1
        assert report.total_active_consumers == 2
        assert len(report.endpoints) == 2

    def test_report_endpoint_details(self):
        t = ApiDeprecationTracker()
        now = datetime.now(UTC)
        t.deprecate("GET /api/v1/old", sunset_at=now + timedelta(days=15),
                     replacement="/api/v2/new")
        for _ in range(5):
            t.check("GET /api/v1/old", "client-1")

        report = t.get_report(now=now)
        ep = report.endpoints[0]
        assert ep["endpoint"] == "GET /api/v1/old"
        assert ep["consumer_count"] == 1
        assert ep["total_calls"] == 5
        assert ep["days_until_sunset"] == 15
        assert ep["replacement"] == "/api/v2/new"

    def test_filter_by_phase(self):
        t = ApiDeprecationTracker()
        now = datetime.now(UTC)
        t.deprecate("GET /a", sunset_at=now + timedelta(days=30))
        t.deprecate("GET /b", sunset_at=now + timedelta(days=60))
        t.remove("GET /b")
        deprecated = t.list_notices(DeprecationPhase.DEPRECATED)
        assert len(deprecated) == 1
        removed = t.list_notices(DeprecationPhase.REMOVED)
        assert len(removed) == 1
