"""Tests for Endpoint Circuit Breaker Dashboard service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_circuit_dashboard import (
    CircuitDashboard, CircuitBreaker,
)


class TestCircuitDashboard:
    def test_register_and_overview(self):
        svc = CircuitDashboard()
        svc.register(CircuitBreaker("c1", "ep1"))
        svc.register(CircuitBreaker("c2", "ep2"))
        overview = svc.get_overview()
        assert overview["total"] == 2
        assert overview["closed"] == 2

    def test_trip_circuit(self):
        svc = CircuitDashboard()
        svc.register(CircuitBreaker("c1", "ep1", failure_threshold=3))
        for _ in range(3):
            svc.record_failure("c1")
        cb = svc.get_circuit("c1")
        assert cb["state"] == "open"
        assert cb["total_trips"] == 1

    def test_half_open_recovery(self):
        svc = CircuitDashboard()
        svc.register(CircuitBreaker("c1", "ep1", failure_threshold=2, half_open_max=2))
        svc.record_failure("c1")
        svc.record_failure("c1")
        svc.attempt_reset("c1")
        svc.record_success("c1")
        svc.record_success("c1")
        assert svc.get_circuit("c1")["state"] == "closed"

    def test_half_open_failure_reopens(self):
        svc = CircuitDashboard()
        svc.register(CircuitBreaker("c1", "ep1", failure_threshold=1))
        svc.record_failure("c1")
        svc.attempt_reset("c1")
        svc.record_failure("c1")
        assert svc.get_circuit("c1")["state"] == "open"

    def test_force_close(self):
        svc = CircuitDashboard()
        svc.register(CircuitBreaker("c1", "ep1", failure_threshold=1))
        svc.record_failure("c1")
        svc.force_close("c1")
        assert svc.get_circuit("c1")["state"] == "closed"

    def test_list_by_state(self):
        svc = CircuitDashboard()
        svc.register(CircuitBreaker("c1", "ep1"))
        svc.register(CircuitBreaker("c2", "ep2", failure_threshold=1))
        svc.record_failure("c2")
        open_circuits = svc.list_circuits(state="open")
        assert len(open_circuits) == 1
        assert open_circuits[0]["circuit_id"] == "c2"

    def test_success_decrements_failures(self):
        svc = CircuitDashboard()
        svc.register(CircuitBreaker("c1", "ep1", failure_threshold=5))
        svc.record_failure("c1")
        svc.record_failure("c1")
        svc.record_success("c1")
        assert svc.get_circuit("c1")["failure_count"] == 1

    def test_attempt_reset_not_open(self):
        svc = CircuitDashboard()
        svc.register(CircuitBreaker("c1", "ep1"))
        result = svc.attempt_reset("c1")
        assert result["error"] == "not_open"

    def test_duplicate_circuit(self):
        svc = CircuitDashboard()
        svc.register(CircuitBreaker("c1", "ep1"))
        with pytest.raises(ValueError):
            svc.register(CircuitBreaker("c1", "ep2"))

    def test_not_found(self):
        svc = CircuitDashboard()
        assert svc.get_circuit("missing") is None

    def test_isolation(self):
        a, b = CircuitDashboard(), CircuitDashboard()
        a.register(CircuitBreaker("c1", "ep1"))
        assert b.get_overview()["total"] == 0
