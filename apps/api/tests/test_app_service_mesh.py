"""Tests for App Service Mesh — routes, blocking, requests."""

import pytest

from app.services.app_service_mesh import AppServiceMesh


class TestAddRoute:
    def test_add(self):
        m = AppServiceMesh()
        r = m.add_route("inst-1", "api", "db", timeout_ms=3000, max_retries=2)
        assert r.source == "api"
        assert r.destination == "db"
        assert r.allowed is True

    def test_self_route(self):
        m = AppServiceMesh()
        with pytest.raises(ValueError, match="differ"):
            m.add_route("inst-1", "api", "api")

    def test_duplicate(self):
        m = AppServiceMesh()
        m.add_route("inst-1", "api", "db")
        with pytest.raises(ValueError, match="already exists"):
            m.add_route("inst-1", "api", "db")


class TestCommunication:
    def test_allowed(self):
        m = AppServiceMesh()
        m.add_route("inst-1", "api", "db")
        assert m.can_communicate("inst-1", "api", "db") is True

    def test_no_route_denied(self):
        m = AppServiceMesh()
        assert m.can_communicate("inst-1", "api", "db") is False

    def test_blocked(self):
        m = AppServiceMesh()
        m.add_route("inst-1", "api", "db")
        m.block_route("inst-1", "api", "db")
        assert m.can_communicate("inst-1", "api", "db") is False

    def test_reallow(self):
        m = AppServiceMesh()
        m.add_route("inst-1", "api", "db")
        m.block_route("inst-1", "api", "db")
        m.allow_route("inst-1", "api", "db")
        assert m.can_communicate("inst-1", "api", "db") is True


class TestRequestTracking:
    def test_record(self):
        m = AppServiceMesh()
        m.add_route("inst-1", "api", "db")
        count = m.record_request("inst-1", "api", "db")
        assert count == 1
        count = m.record_request("inst-1", "api", "db")
        assert count == 2

    def test_blocked_route_rejects(self):
        m = AppServiceMesh()
        m.add_route("inst-1", "api", "db")
        m.block_route("inst-1", "api", "db")
        with pytest.raises(ValueError, match="blocked"):
            m.record_request("inst-1", "api", "db")


class TestRouteQueries:
    def test_routes_from(self):
        m = AppServiceMesh()
        m.add_route("inst-1", "api", "db")
        m.add_route("inst-1", "api", "cache")
        m.add_route("inst-1", "worker", "db")
        routes = m.get_routes_from("inst-1", "api")
        assert len(routes) == 2

    def test_routes_to(self):
        m = AppServiceMesh()
        m.add_route("inst-1", "api", "db")
        m.add_route("inst-1", "worker", "db")
        routes = m.get_routes_to("inst-1", "db")
        assert len(routes) == 2


class TestIsolation:
    def test_cross_installation(self):
        m = AppServiceMesh()
        m.add_route("inst-1", "api", "db")
        assert m.can_communicate("inst-2", "api", "db") is False
