"""Tests for App API Playground Session — create, history, expire."""

import pytest

from app.services.app_api_playground_session import AppAPIPlaygroundSession


class TestCreate:
    def test_create(self):
        p = AppAPIPlaygroundSession()
        s = p.create("inst-1", "s1", "user-1")
        assert s.active is True
        assert s.request_count == 0

    def test_duplicate(self):
        p = AppAPIPlaygroundSession()
        p.create("inst-1", "s1", "user-1")
        with pytest.raises(ValueError, match="already exists"):
            p.create("inst-1", "s1", "user-2")


class TestHistory:
    def test_add_request(self):
        p = AppAPIPlaygroundSession()
        p.create("inst-1", "s1", "user-1")
        s = p.add_request("inst-1", "s1", "user-1", "GET", "/api/users", 200, 45.0)
        assert s.request_count == 1

    def test_ended_rejects(self):
        p = AppAPIPlaygroundSession()
        p.create("inst-1", "s1", "user-1")
        p.end("inst-1", "s1", "user-1")
        with pytest.raises(ValueError, match="expired"):
            p.add_request("inst-1", "s1", "user-1", "GET", "/api", 200, 10)


class TestActive:
    def test_active(self):
        p = AppAPIPlaygroundSession()
        p.create("inst-1", "s1", "user-1")
        p.create("inst-1", "s2", "user-2")
        p.end("inst-1", "s1", "user-1")
        assert len(p.active_sessions("inst-1")) == 1


class TestIsolation:
    def test_cross(self):
        p = AppAPIPlaygroundSession()
        p.create("inst-1", "s1", "user-1")
        assert p.list_sessions("inst-2") == []
