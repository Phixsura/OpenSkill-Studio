"""Tests for App API Error Code — define, lookup, categories."""

import pytest

from app.services.app_api_error_code import AppAPIErrorCode


class TestDefine:
    def test_define(self):
        e = AppAPIErrorCode()
        ec = e.define("inst-1", "AUTH_EXPIRED", "Token expired", 401, "auth")
        assert ec.http_status == 401

    def test_duplicate(self):
        e = AppAPIErrorCode()
        e.define("inst-1", "AUTH_EXPIRED", "Expired", 401)
        with pytest.raises(ValueError, match="already defined"):
            e.define("inst-1", "AUTH_EXPIRED", "Dup", 401)

    def test_invalid_status(self):
        e = AppAPIErrorCode()
        with pytest.raises(ValueError, match="4xx or 5xx"):
            e.define("inst-1", "OK", "OK", 200)


class TestLookup:
    def test_found(self):
        e = AppAPIErrorCode()
        e.define("inst-1", "NOT_FOUND", "Resource not found", 404)
        ec = e.lookup("inst-1", "NOT_FOUND")
        assert ec.message == "Resource not found"

    def test_by_category(self):
        e = AppAPIErrorCode()
        e.define("inst-1", "AUTH_EXPIRED", "Expired", 401, "auth")
        e.define("inst-1", "RATE_LIMIT", "Too many", 429, "rate")
        assert len(e.by_category("inst-1", "auth")) == 1


class TestIsolation:
    def test_cross(self):
        e = AppAPIErrorCode()
        e.define("inst-1", "ERR", "Error", 500)
        assert e.list_codes("inst-2") == []
