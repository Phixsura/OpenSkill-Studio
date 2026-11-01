"""Tests for App API Access Log — log, filter, actors."""

from app.services.app_api_access_log import AppAPIAccessLog


class TestLog:
    def test_log(self):
        l = AppAPIAccessLog()
        e = l.log("inst-1", "l1", "alice", "GET", "/api/users", 200, "10.0.0.1")
        assert e.actor == "alice"


class TestFilter:
    def test_by_actor(self):
        l = AppAPIAccessLog()
        l.log("inst-1", "l1", "alice", "GET", "/api", 200)
        l.log("inst-1", "l2", "bob", "POST", "/api", 201)
        assert len(l.by_actor("inst-1", "alice")) == 1

    def test_by_ip(self):
        l = AppAPIAccessLog()
        l.log("inst-1", "l1", "alice", "GET", "/api", 200, "10.0.0.1")
        l.log("inst-1", "l2", "bob", "GET", "/api", 200, "10.0.0.2")
        assert len(l.by_ip("inst-1", "10.0.0.1")) == 1

    def test_unique_actors(self):
        l = AppAPIAccessLog()
        l.log("inst-1", "l1", "alice", "GET", "/api", 200)
        l.log("inst-1", "l2", "bob", "GET", "/api", 200)
        l.log("inst-1", "l3", "alice", "POST", "/api", 201)
        assert l.unique_actors("inst-1") == ["alice", "bob"]


class TestIsolation:
    def test_cross(self):
        l = AppAPIAccessLog()
        l.log("inst-1", "l1", "alice", "GET", "/api", 200)
        assert l.count("inst-2") == 0
