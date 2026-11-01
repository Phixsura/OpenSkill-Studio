"""Tests for Endpoint Traffic Shaper service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_traffic_shaper import (
    TrafficShaper, TrafficRule,
)


class TestTrafficShaper:
    def test_admit_basic(self):
        svc = TrafficShaper()
        svc.set_rule(TrafficRule("r1", "c1", "normal", 100))
        result = svc.admit("c1")
        assert result["admitted"] is True
        assert result["priority"] == "normal"

    def test_consumer_limit(self):
        svc = TrafficShaper()
        svc.set_rule(TrafficRule("r1", "c1", "normal", 2))
        svc.admit("c1")
        svc.admit("c1")
        result = svc.admit("c1")
        assert result["admitted"] is False
        assert result["reason"] == "consumer_limit"

    def test_global_limit(self):
        svc = TrafficShaper()
        svc.configure_global(3)
        svc.set_rule(TrafficRule("r1", "c1", "normal", 100))
        svc.admit("c1")
        svc.admit("c1")
        svc.admit("c1")
        result = svc.admit("c1")
        assert result["admitted"] is False
        assert result["reason"] == "global_limit"

    def test_critical_bypasses_global(self):
        svc = TrafficShaper()
        svc.configure_global(2)
        svc.set_rule(TrafficRule("r1", "c1", "critical", 100))
        svc.set_rule(TrafficRule("r2", "c2", "normal", 100))
        svc.admit("c2")
        svc.admit("c2")
        result = svc.admit("c1")
        assert result["admitted"] is True
        assert result["bypassed_global"] is True

    def test_reset_window(self):
        svc = TrafficShaper()
        svc.set_rule(TrafficRule("r1", "c1", "normal", 2))
        svc.admit("c1")
        svc.admit("c1")
        svc.reset_window()
        result = svc.admit("c1")
        assert result["admitted"] is True

    def test_unknown_consumer(self):
        svc = TrafficShaper()
        result = svc.admit("unknown")
        assert result["admitted"] is True
        assert result["priority"] == "normal"

    def test_consumer_status(self):
        svc = TrafficShaper()
        svc.set_rule(TrafficRule("r1", "c1", "high", 50))
        svc.admit("c1")
        status = svc.get_consumer_status("c1")
        assert status["current_rps"] == 1
        assert status["status"] == "flowing"

    def test_overview(self):
        svc = TrafficShaper()
        svc.set_rule(TrafficRule("r1", "c1", "critical", 100))
        svc.set_rule(TrafficRule("r2", "c2", "normal", 50))
        overview = svc.get_overview()
        assert overview["consumers"] == 2
        assert overview["by_priority"]["critical"] == 1

    def test_invalid_priority(self):
        svc = TrafficShaper()
        with pytest.raises(ValueError):
            svc.set_rule(TrafficRule("r1", "c1", "ultra", 100))

    def test_throttled_count(self):
        svc = TrafficShaper()
        svc.set_rule(TrafficRule("r1", "c1", "low", 1))
        svc.admit("c1")
        svc.admit("c1")
        svc.admit("c1")
        status = svc.get_consumer_status("c1")
        assert status["throttled_count"] == 2

    def test_isolation(self):
        a, b = TrafficShaper(), TrafficShaper()
        a.set_rule(TrafficRule("r1", "c1", "normal", 100))
        assert b.get_consumer_status("c1")["status"] == "no_rule"
