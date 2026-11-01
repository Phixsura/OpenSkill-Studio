"""Tests for App API Request Log — log, filter, stats."""

from app.services.app_api_request_log import AppAPIRequestLog


class TestLog:
    def test_log(self):
        l = AppAPIRequestLog()
        e = l.log_request("inst-1", "l1", "GET", "/api/users", 200, 45.0)
        assert e.method == "GET"


class TestQuery:
    def test_errors(self):
        l = AppAPIRequestLog()
        l.log_request("inst-1", "l1", "GET", "/api/users", 200, 45)
        l.log_request("inst-1", "l2", "POST", "/api/users", 400, 10)
        l.log_request("inst-1", "l3", "GET", "/api/apps", 500, 100)
        assert len(l.errors("inst-1")) == 2

    def test_path_stats(self):
        l = AppAPIRequestLog()
        l.log_request("inst-1", "l1", "GET", "/api/users", 200, 50)
        l.log_request("inst-1", "l2", "GET", "/api/users", 200, 100)
        l.log_request("inst-1", "l3", "GET", "/api/apps", 200, 30)
        stats = l.path_stats("inst-1")
        assert stats[0]["path"] == "/api/users"
        assert stats[0]["avg_ms"] == 75.0


class TestIsolation:
    def test_cross(self):
        l = AppAPIRequestLog()
        l.log_request("inst-1", "l1", "GET", "/api", 200, 10)
        assert l.count("inst-2") == 0
