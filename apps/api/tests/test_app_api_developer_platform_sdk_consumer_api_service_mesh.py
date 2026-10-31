"""Tests for Endpoint Service Mesh service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_service_mesh import (
    ServiceMesh, ServiceNode, ServiceLink,
)


class TestServiceMesh:
    def _setup(self):
        svc = ServiceMesh()
        svc.register_service(ServiceNode("auth", "Auth Service"))
        svc.register_service(ServiceNode("users", "Users Service"))
        svc.register_service(ServiceNode("orders", "Orders Service"))
        svc.add_link(ServiceLink("users", "auth"))
        svc.add_link(ServiceLink("orders", "users"))
        return svc

    def test_route_request(self):
        svc = self._setup()
        result = svc.route_request("users", "auth")
        assert result["routed"] is True

    def test_no_link(self):
        svc = self._setup()
        result = svc.route_request("auth", "orders")
        assert result["routed"] is False
        assert result["reason"] == "no_link"

    def test_unhealthy_target(self):
        svc = self._setup()
        svc._nodes["auth"].healthy = False
        result = svc.route_request("users", "auth")
        assert result["routed"] is False
        assert result["reason"] == "target_unhealthy"

    def test_circuit_breaker(self):
        svc = self._setup()
        link = svc._links["users->auth"]
        link.failure_threshold = 3
        for _ in range(3):
            svc.record_failure("users", "auth")
        result = svc.route_request("users", "auth")
        assert result["routed"] is False
        assert result["reason"] == "circuit_open"

    def test_reset_circuit(self):
        svc = self._setup()
        svc._links["users->auth"].failure_threshold = 1
        svc.record_failure("users", "auth")
        svc.reset_circuit("users", "auth")
        result = svc.route_request("users", "auth")
        assert result["routed"] is True

    def test_topology(self):
        svc = self._setup()
        topo = svc.get_topology()
        assert len(topo["nodes"]) == 3
        assert len(topo["links"]) == 2

    def test_service_deps(self):
        svc = self._setup()
        deps = svc.get_service_deps("users")
        assert "orders" in deps["upstream"]
        assert "auth" in deps["downstream"]

    def test_stats(self):
        svc = self._setup()
        stats = svc.get_stats()
        assert stats["total_services"] == 3
        assert stats["total_links"] == 2
        assert stats["open_circuits"] == 0

    def test_duplicate_service(self):
        svc = ServiceMesh()
        svc.register_service(ServiceNode("a", "A"))
        with pytest.raises(ValueError):
            svc.register_service(ServiceNode("a", "A2"))

    def test_link_missing_service(self):
        svc = ServiceMesh()
        svc.register_service(ServiceNode("a", "A"))
        with pytest.raises(ValueError):
            svc.add_link(ServiceLink("a", "missing"))

    def test_isolation(self):
        a = self._setup()
        b = ServiceMesh()
        assert b.get_stats()["total_services"] == 0
