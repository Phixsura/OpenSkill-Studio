"""Tests for App Load Balancer — routing, health, weights."""

import pytest

from app.services.app_load_balancer import AppLoadBalancer


class TestAdd:
    def test_add(self):
        lb = AppLoadBalancer()
        inst = lb.add_instance("inst-1", "i1", "10.0.0.1:8080")
        assert inst.healthy is True

    def test_duplicate(self):
        lb = AppLoadBalancer()
        lb.add_instance("inst-1", "i1", "10.0.0.1:8080")
        with pytest.raises(ValueError, match="already exists"):
            lb.add_instance("inst-1", "i1", "10.0.0.2:8080")


class TestRouting:
    def test_round_robin(self):
        lb = AppLoadBalancer()
        lb.add_instance("inst-1", "i1", "10.0.0.1:8080")
        lb.add_instance("inst-1", "i2", "10.0.0.2:8080")
        results = [lb.next_instance("inst-1").instance_id for _ in range(4)]
        assert results == ["i1", "i2", "i1", "i2"]

    def test_weighted(self):
        lb = AppLoadBalancer()
        lb.add_instance("inst-1", "i1", "10.0.0.1:8080", weight=2)
        lb.add_instance("inst-1", "i2", "10.0.0.2:8080", weight=1)
        results = [lb.next_instance("inst-1").instance_id for _ in range(3)]
        assert results == ["i1", "i1", "i2"]

    def test_skip_unhealthy(self):
        lb = AppLoadBalancer()
        lb.add_instance("inst-1", "i1", "10.0.0.1:8080")
        lb.add_instance("inst-1", "i2", "10.0.0.2:8080")
        lb.set_health("inst-1", "i1", False)
        inst = lb.next_instance("inst-1")
        assert inst.instance_id == "i2"

    def test_no_healthy(self):
        lb = AppLoadBalancer()
        lb.add_instance("inst-1", "i1", "10.0.0.1:8080")
        lb.set_health("inst-1", "i1", False)
        with pytest.raises(ValueError, match="No healthy"):
            lb.next_instance("inst-1")


class TestIsolation:
    def test_cross(self):
        lb = AppLoadBalancer()
        lb.add_instance("inst-1", "i1", "10.0.0.1:8080")
        assert lb.list_instances("inst-2") == []
