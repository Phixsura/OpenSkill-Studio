"""Tests for App Access Log — record, query, endpoint stats, error rate."""

import pytest

from app.services.app_access_log import AppAccessLog


class TestRecord:
    def test_record(self):
        l = AppAccessLog()
        e = l.record("inst-1", "r1", "GET", "/api/users", 200, 42.5, now=1000.0)
        assert e.method == "GET"
        assert e.path == "/api/users"
        assert e.status_code == 200

    def test_uppercases_method(self):
        l = AppAccessLog()
        e = l.record("inst-1", "r1", "post", "/api", 201, 10.0)
        assert e.method == "POST"

    def test_invalid_status(self):
        l = AppAccessLog()
        with pytest.raises(ValueError, match="status_code"):
            l.record("inst-1", "r1", "GET", "/", 999, 0)

    def test_missing_path(self):
        l = AppAccessLog()
        with pytest.raises(ValueError, match="path"):
            l.record("inst-1", "r1", "GET", "", 200, 0)


class TestQuery:
    def test_basic_query(self):
        l = AppAccessLog()
        l.record("inst-1", "r1", "GET", "/a", 200, 10, now=1000.0)
        l.record("inst-1", "r2", "GET", "/b", 200, 20, now=1001.0)
        results = l.query("inst-1")
        assert len(results) == 2
        assert results[0].entry_id == "r2"  # newest first

    def test_filter_method(self):
        l = AppAccessLog()
        l.record("inst-1", "r1", "GET", "/a", 200, 10)
        l.record("inst-1", "r2", "POST", "/a", 201, 20)
        results = l.query("inst-1", method="GET")
        assert len(results) == 1

    def test_filter_path(self):
        l = AppAccessLog()
        l.record("inst-1", "r1", "GET", "/users", 200, 10)
        l.record("inst-1", "r2", "GET", "/posts", 200, 20)
        results = l.query("inst-1", path="/users")
        assert len(results) == 1

    def test_filter_status_range(self):
        l = AppAccessLog()
        l.record("inst-1", "r1", "GET", "/a", 200, 10)
        l.record("inst-1", "r2", "GET", "/b", 404, 20)
        l.record("inst-1", "r3", "GET", "/c", 500, 30)
        results = l.query("inst-1", status_min=400)
        assert len(results) == 2

    def test_query_limit(self):
        l = AppAccessLog()
        for i in range(10):
            l.record("inst-1", f"r{i}", "GET", "/a", 200, 10)
        results = l.query("inst-1", limit=3)
        assert len(results) == 3


class TestEndpointStats:
    def test_stats(self):
        l = AppAccessLog()
        l.record("inst-1", "r1", "GET", "/api", 200, 10)
        l.record("inst-1", "r2", "GET", "/api", 200, 20)
        l.record("inst-1", "r3", "GET", "/api", 500, 30)
        stats = l.get_endpoint_stats("inst-1")
        assert len(stats) == 1
        s = stats[0]
        assert s.total_requests == 3
        assert s.error_count == 1
        assert s.avg_response_ms == 20.0
        assert s.error_rate_pct == pytest.approx(33.33, abs=0.01)


class TestErrorRate:
    def test_error_rate(self):
        l = AppAccessLog()
        l.record("inst-1", "r1", "GET", "/a", 200, 10)
        l.record("inst-1", "r2", "GET", "/b", 500, 20)
        assert l.error_rate("inst-1") == 50.0

    def test_no_entries(self):
        l = AppAccessLog()
        assert l.error_rate("inst-1") == 0.0


class TestIsolation:
    def test_cross_installation(self):
        l = AppAccessLog()
        l.record("inst-1", "r1", "GET", "/a", 200, 10)
        assert l.count("inst-2") == 0
        assert l.query("inst-2") == []
