"""Tests for App Load Balancer — round-robin, weights, health, routing."""

import pytest

from app.services.app_load_balancer import AppLoadBalancer


class TestAddInstance:
    def test_add(self):
        lb = AppLoadBalancer()
        inst = lb.add_instance("inst-1", "i1", "10.0.0.1:8080")
        assert inst.address == "10.0.0.1:8080"
        assert inst.healthy is True

    def test_duplicate(self):
        lb = AppLoadBalancer()
        lb.add_instance("inst-1", "i1", "10.0.0.1:8080")
        with pytest.raises(ValueError, match="already exists"):
            lb.add_instance("inst-1", "i1", "10.0.0.2:8080")

    def test_invalid_weight(self):
        lb = AppLoadBalancer()
        with pytest.raises(ValueError, match="weight"):
            lb.add_instance("inst-1", "i1", "10.0.0.1", weight=0)


class TestNextInstance:
    def test_round_robin(self):
        lb = AppLoadBalancer()
        lb.add_instance("inst-1", "i1", "10.0.0.1")
        lb.add_instance("inst-1", "i2", "10.0.0.2")
        first = lb.next_instance("inst-1")
        second = lb.next_instance("inst-1")
        assert first.instance_id != second.instance_id

    def test_skips_unhealthy(self):
        lb = AppLoadBalancer()
        lb.add_instance("inst-1", "i1", "10.0.0.1")
        lb.add_instance("inst-1", "i2", "10.0.0.2")
        lb.mark_unhealthy("inst-1", "i1")
        inst = lb.next_instance("inst-1")
        assert inst.instance_id == "i2"

    def test_no_healthy(self):
        lb = AppLoadBalancer()
        lb.add_instance("inst-1", "i1", "10.0.0.1")
        lb.mark_unhealthy("inst-1", "i1")
        with pytest.raises(ValueError, match="No healthy"):
            lb.next_instance("inst-1")

    def test_weighted(self):
        lb = AppLoadBalancer()
        lb.add_instance("inst-1", "heavy", "10.0.0.1", weight=3)
        lb.add_instance("inst-1", "light", "10.0.0.2", weight=1)
        counts = {"heavy": 0, "light": 0}
        for _ in range(40):
            inst = lb.next_instance("inst-1")
            counts[inst.instance_id] += 1
        assert counts["heavy"] > counts["light"]

    def test_tracks_request_count(self):
        lb = AppLoadBalancer()
        lb.add_instance("inst-1", "i1", "10.0.0.1")
        lb.next_instance("inst-1")
        lb.next_instance("inst-1")
        pool = lb.get_pool("inst-1")
        assert pool[0].request_count == 2


class TestHealth:
    def test_mark_healthy(self):
        lb = AppLoadBalancer()
        lb.add_instance("inst-1", "i1", "10.0.0.1")
        lb.mark_unhealthy("inst-1", "i1")
        lb.mark_healthy("inst-1", "i1")
        inst = lb.next_instance("inst-1")
        assert inst.instance_id == "i1"


class TestRemove:
    def test_remove(self):
        lb = AppLoadBalancer()
        lb.add_instance("inst-1", "i1", "10.0.0.1")
        assert lb.remove_instance("inst-1", "i1") is True
        assert lb.get_pool("inst-1") == []

    def test_remove_nonexistent(self):
        lb = AppLoadBalancer()
        assert lb.remove_instance("inst-1", "nope") is False


class TestIsolation:
    def test_cross_installation(self):
        lb = AppLoadBalancer()
        lb.add_instance("inst-1", "i1", "10.0.0.1")
        assert lb.get_pool("inst-2") == []
