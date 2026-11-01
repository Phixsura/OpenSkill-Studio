"""Tests for API Mock Server service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_mock_server import (
    MockServer, MockResponse,
)


class TestMockServer:
    def test_register_and_handle(self):
        svc = MockServer()
        svc.register("/api/users", "GET", MockResponse(200, {"users": []}))
        result = svc.handle_request("GET", "/api/users")
        assert result["status_code"] == 200
        assert result["body"] == {"users": []}
        assert result["matched"] is True

    def test_not_found(self):
        svc = MockServer()
        result = svc.handle_request("GET", "/missing")
        assert result["status_code"] == 404
        assert result["matched"] is False

    def test_pattern_matching(self):
        svc = MockServer()
        svc.register("/api/users/{id}", "GET", MockResponse(200, {"id": "123"}))
        result = svc.handle_request("GET", "/api/users/abc")
        assert result["matched"] is True

    def test_hit_count(self):
        svc = MockServer()
        svc.register("/api/data", "POST", MockResponse(201, {"ok": True}))
        svc.handle_request("POST", "/api/data")
        svc.handle_request("POST", "/api/data")
        endpoints = svc.list_endpoints()
        assert endpoints[0]["hit_count"] == 2

    def test_disabled_endpoint(self):
        svc = MockServer()
        svc.register("/api/test", "GET")
        svc.set_enabled("GET", "/api/test", False)
        result = svc.handle_request("GET", "/api/test")
        assert result["matched"] is False

    def test_custom_headers_and_delay(self):
        svc = MockServer()
        resp = MockResponse(200, "ok", {"X-Custom": "val"}, delay_ms=100)
        svc.register("/api/slow", "GET", resp)
        result = svc.handle_request("GET", "/api/slow")
        assert result["headers"]["X-Custom"] == "val"
        assert result["delay_ms"] == 100

    def test_stats(self):
        svc = MockServer()
        svc.register("/a", "GET")
        svc.register("/b", "POST")
        svc.handle_request("GET", "/a")
        svc.handle_request("GET", "/missing")
        stats = svc.get_stats()
        assert stats["total_endpoints"] == 2
        assert stats["total_requests"] == 2
        assert stats["unmatched"] == 1

    def test_reset_counts(self):
        svc = MockServer()
        svc.register("/a", "GET")
        svc.handle_request("GET", "/a")
        svc.reset_counts()
        assert svc.get_stats()["total_hits"] == 0

    def test_invalid_path(self):
        svc = MockServer()
        with pytest.raises(ValueError):
            svc.register("no-slash", "GET")

    def test_invalid_method(self):
        svc = MockServer()
        with pytest.raises(ValueError):
            svc.register("/api", "TRACE")

    def test_isolation(self):
        a, b = MockServer(), MockServer()
        a.register("/x", "GET")
        assert b.handle_request("GET", "/x")["matched"] is False
