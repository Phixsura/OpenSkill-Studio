"""Tests for Endpoint Load Balancer service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_load_balancer import (
    LoadBalancer, BackendTarget,
)


class TestLoadBalancer:
    def test_add_and_route(self):
        svc = LoadBalancer()
        svc.add_target(BackendTarget("t1", "http://a:8080"))
        result = svc.route()
        assert result is not None
        assert result["target_id"] == "t1"

    def test_round_robin(self):
        svc = LoadBalancer()
        svc.add_target(BackendTarget("t1", "http://a:8080"))
        svc.add_target(BackendTarget("t2", "http://b:8080"))
        ids = [svc.route()["target_id"] for _ in range(4)]
        assert "t1" in ids and "t2" in ids

    def test_weighted_routing(self):
        svc = LoadBalancer()
        svc.add_target(BackendTarget("t1", "http://a", weight=3))
        svc.add_target(BackendTarget("t2", "http://b", weight=1))
        counts = {"t1": 0, "t2": 0}
        for _ in range(8):
            r = svc.route()
            counts[r["target_id"]] += 1
        assert counts["t1"] > counts["t2"]

    def test_health_aware(self):
        svc = LoadBalancer()
        svc.add_target(BackendTarget("t1", "http://a"))
        svc.add_target(BackendTarget("t2", "http://b"))
        svc.set_health("t1", False)
        for _ in range(5):
            result = svc.route()
            assert result["target_id"] == "t2"

    def test_no_healthy_targets(self):
        svc = LoadBalancer()
        svc.add_target(BackendTarget("t1", "http://a"))
        svc.set_health("t1", False)
        assert svc.route() is None

    def test_least_connections(self):
        svc = LoadBalancer()
        svc.set_algorithm("least_connections")
        svc.add_target(BackendTarget("t1", "http://a"))
        svc.add_target(BackendTarget("t2", "http://b"))
        svc.route()  # t1 gets 1 conn
        result = svc.route()
        assert result["target_id"] == "t2"

    def test_release(self):
        svc = LoadBalancer()
        svc.add_target(BackendTarget("t1", "http://a"))
        svc.route()
        svc.release("t1")
        targets = svc.list_targets()
        assert targets[0]["connections"] == 0

    def test_remove_target(self):
        svc = LoadBalancer()
        svc.add_target(BackendTarget("t1", "http://a"))
        result = svc.remove_target("t1")
        assert result["removed"] is True
        assert svc.route() is None

    def test_stats(self):
        svc = LoadBalancer()
        svc.add_target(BackendTarget("t1", "http://a"))
        svc.add_target(BackendTarget("t2", "http://b"))
        svc.set_health("t2", False)
        stats = svc.get_stats()
        assert stats["healthy"] == 1
        assert stats["unhealthy"] == 1

    def test_duplicate_target(self):
        svc = LoadBalancer()
        svc.add_target(BackendTarget("t1", "http://a"))
        with pytest.raises(ValueError):
            svc.add_target(BackendTarget("t1", "http://b"))

    def test_isolation(self):
        a, b = LoadBalancer(), LoadBalancer()
        a.add_target(BackendTarget("t1", "http://a"))
        assert b.route() is None
