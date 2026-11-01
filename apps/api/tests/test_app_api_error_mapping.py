"""Tests for App API Error Mapping — define, resolve, top errors."""

import pytest
from app.services.app_api_error_mapping import AppAPIErrorMapping


class TestDefine:
    def test_define(self):
        m = AppAPIErrorMapping()
        em = m.define("inst-1", "DB_TIMEOUT", "SERVICE_UNAVAILABLE", 503, "Service temporarily unavailable")
        assert em.http_status == 503


class TestResolve:
    def test_resolve(self):
        m = AppAPIErrorMapping()
        m.define("inst-1", "DB_TIMEOUT", "SERVICE_UNAVAILABLE", 503, "Unavailable")
        em = m.resolve("inst-1", "DB_TIMEOUT")
        assert em is not None
        assert em.public_code == "SERVICE_UNAVAILABLE"
        assert em.occurrences == 1

    def test_unmapped(self):
        m = AppAPIErrorMapping()
        assert m.resolve("inst-1", "UNKNOWN") is None

    def test_top_errors(self):
        m = AppAPIErrorMapping()
        m.define("inst-1", "A", "PUB_A", 500, "A")
        m.define("inst-1", "B", "PUB_B", 400, "B")
        for _ in range(5):
            m.resolve("inst-1", "A")
        for _ in range(2):
            m.resolve("inst-1", "B")
        top = m.top_errors("inst-1")
        assert top[0].internal_code == "A"


class TestIsolation:
    def test_cross(self):
        m = AppAPIErrorMapping()
        m.define("inst-1", "A", "B", 500, "M")
        assert m.list_mappings("inst-2") == []
