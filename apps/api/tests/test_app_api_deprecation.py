"""Tests for App API Deprecation — deprecate, headers, sunset."""

import time

import pytest

from app.services.app_api_deprecation import AppAPIDeprecation


FUTURE = time.time() + 86400 * 90  # 90 days


class TestDeprecate:
    def test_deprecate(self):
        d = AppAPIDeprecation()
        ep = d.deprecate("inst-1", "ep1", "GET", "/api/v1/users", FUTURE, "/api/v2/users")
        assert ep.method == "GET"
        assert ep.days_until_sunset > 0

    def test_past_sunset(self):
        d = AppAPIDeprecation()
        with pytest.raises(ValueError, match="future"):
            d.deprecate("inst-1", "ep1", "GET", "/api/v1/users", time.time() - 100)


class TestHeaders:
    def test_headers(self):
        d = AppAPIDeprecation()
        d.deprecate("inst-1", "ep1", "GET", "/api/v1/users", FUTURE, "/api/v2/users")
        headers = d.deprecation_headers("inst-1", "ep1")
        assert headers["Deprecation"] == "true"
        assert "successor-version" in headers["Link"]

    def test_no_replacement(self):
        d = AppAPIDeprecation()
        d.deprecate("inst-1", "ep1", "GET", "/api/v1/old", FUTURE)
        headers = d.deprecation_headers("inst-1", "ep1")
        assert "Link" not in headers


class TestRequest:
    def test_count(self):
        d = AppAPIDeprecation()
        d.deprecate("inst-1", "ep1", "GET", "/api/v1/users", FUTURE)
        d.record_request("inst-1", "ep1")
        d.record_request("inst-1", "ep1")
        ep = d.list_all("inst-1")[0]
        assert ep.request_count == 2


class TestActive:
    def test_active(self):
        d = AppAPIDeprecation()
        d.deprecate("inst-1", "ep1", "GET", "/api/v1/users", FUTURE)
        assert len(d.active_deprecations("inst-1")) == 1
        assert len(d.sunset_endpoints("inst-1")) == 0


class TestIsolation:
    def test_cross(self):
        d = AppAPIDeprecation()
        d.deprecate("inst-1", "ep1", "GET", "/api/v1/users", FUTURE)
        assert d.list_all("inst-2") == []
