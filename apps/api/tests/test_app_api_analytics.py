"""Tests for App API Analytics — recording, rankings, peak hours."""

import pytest

from app.services.app_api_analytics import AppAPIAnalytics


class TestRecord:
    def test_record(self):
        a = AppAPIAnalytics()
        a.record_request("inst-1", "GET", "/api/users", 200, 45.0, hour=10)
        eps = a.get_top_endpoints("inst-1")
        assert len(eps) == 1
        assert eps[0].total_requests == 1

    def test_accumulates(self):
        a = AppAPIAnalytics()
        a.record_request("inst-1", "GET", "/api", 200, 10.0)
        a.record_request("inst-1", "GET", "/api", 500, 20.0)
        eps = a.get_top_endpoints("inst-1")
        assert eps[0].total_requests == 2
        assert eps[0].total_errors == 1


class TestProperties:
    def test_avg_latency(self):
        a = AppAPIAnalytics()
        a.record_request("inst-1", "GET", "/api", 200, 100.0)
        a.record_request("inst-1", "GET", "/api", 200, 200.0)
        eps = a.get_top_endpoints("inst-1")
        assert eps[0].avg_latency_ms == 150.0

    def test_error_rate(self):
        a = AppAPIAnalytics()
        for _ in range(8):
            a.record_request("inst-1", "GET", "/api", 200, 10.0)
        for _ in range(2):
            a.record_request("inst-1", "GET", "/api", 500, 10.0)
        assert a.get_top_endpoints("inst-1")[0].error_rate_pct == 20.0

    def test_peak_hour(self):
        a = AppAPIAnalytics()
        a.record_request("inst-1", "GET", "/api", 200, 10.0, hour=14)
        a.record_request("inst-1", "GET", "/api", 200, 10.0, hour=14)
        a.record_request("inst-1", "GET", "/api", 200, 10.0, hour=9)
        assert a.get_top_endpoints("inst-1")[0].peak_hour == 14


class TestRankings:
    def test_top_by_requests(self):
        a = AppAPIAnalytics()
        for _ in range(10):
            a.record_request("inst-1", "GET", "/popular", 200, 10.0)
        for _ in range(3):
            a.record_request("inst-1", "GET", "/niche", 200, 10.0)
        top = a.get_top_endpoints("inst-1")
        assert top[0].path == "/popular"

    def test_error_hotspots(self):
        a = AppAPIAnalytics()
        a.record_request("inst-1", "GET", "/good", 200, 10.0)
        a.record_request("inst-1", "GET", "/bad", 500, 10.0)
        hotspots = a.get_error_hotspots("inst-1")
        assert hotspots[0].path == "/bad"

    def test_slowest(self):
        a = AppAPIAnalytics()
        a.record_request("inst-1", "GET", "/fast", 200, 10.0)
        a.record_request("inst-1", "GET", "/slow", 200, 500.0)
        slowest = a.get_slowest("inst-1")
        assert slowest[0].path == "/slow"


class TestIsolation:
    def test_cross_installation(self):
        a = AppAPIAnalytics()
        a.record_request("inst-1", "GET", "/api", 200, 10.0)
        assert a.get_top_endpoints("inst-2") == []
