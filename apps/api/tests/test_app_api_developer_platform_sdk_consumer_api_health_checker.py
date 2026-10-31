"""Tests for Service Health Checker service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_health_checker import (
    HealthChecker, HealthProbe,
)


class TestHealthChecker:
    def test_healthy_endpoint(self):
        svc = HealthChecker()
        for i in range(5):
            svc.record_probe(HealthProbe("ep1", f"t{i}", True, 50.0))
        status = svc.get_status("ep1")
        assert status["status"] == "healthy"
        assert status["uptime_pct"] == 100.0

    def test_degraded_endpoint(self):
        svc = HealthChecker()
        for i in range(9):
            svc.record_probe(HealthProbe("ep1", f"t{i}", True, 50.0))
        svc.record_probe(HealthProbe("ep1", "t9", False, 0.0, error="timeout"))
        status = svc.get_status("ep1")
        assert status["status"] == "degraded"

    def test_circuit_opens(self):
        svc = HealthChecker()
        svc.configure_circuit("ep1", failure_threshold=3)
        for i in range(3):
            result = svc.record_probe(HealthProbe("ep1", f"t{i}", False, 0.0, 500))
        assert result["circuit_state"] == "open"

    def test_circuit_half_open_recovery(self):
        svc = HealthChecker()
        svc.configure_circuit("ep1", failure_threshold=2, recovery_probes=2)
        svc.record_probe(HealthProbe("ep1", "t0", False, 0.0))
        svc.record_probe(HealthProbe("ep1", "t1", False, 0.0))
        assert svc.get_status("ep1")["circuit"] == "open"
        svc.try_half_open("ep1")
        svc.record_probe(HealthProbe("ep1", "t2", True, 30.0))
        svc.record_probe(HealthProbe("ep1", "t3", True, 25.0))
        assert svc.get_status("ep1")["circuit"] == "closed"

    def test_half_open_failure_reopens(self):
        svc = HealthChecker()
        svc.configure_circuit("ep1", failure_threshold=1, recovery_probes=3)
        svc.record_probe(HealthProbe("ep1", "t0", False, 0.0))
        svc.try_half_open("ep1")
        result = svc.record_probe(HealthProbe("ep1", "t1", False, 0.0))
        assert result["circuit_state"] == "open"

    def test_unknown_status(self):
        svc = HealthChecker()
        status = svc.get_status("missing")
        assert status["status"] == "unknown"

    def test_list_endpoints(self):
        svc = HealthChecker()
        svc.record_probe(HealthProbe("ep1", "t0", True, 20.0))
        svc.record_probe(HealthProbe("ep2", "t0", False, 0.0))
        endpoints = svc.list_endpoints()
        assert len(endpoints) == 2
        assert endpoints[0]["uptime_pct"] <= endpoints[1]["uptime_pct"]

    def test_invalid_threshold(self):
        svc = HealthChecker()
        with pytest.raises(ValueError):
            svc.configure_circuit("ep1", failure_threshold=0)

    def test_isolation(self):
        a, b = HealthChecker(), HealthChecker()
        a.record_probe(HealthProbe("ep1", "t0", True, 10.0))
        assert b.get_status("ep1")["status"] == "unknown"
