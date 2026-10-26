from app.services.app_marketplace_extension_sandbox_circuit_breaker import (
    SandboxCircuitBreakerService, CircuitState,
)
import time


def test_register_and_execute():
    svc = SandboxCircuitBreakerService()
    svc.register("sb-1", "api_call")
    result = svc.can_execute("sb-1", "api_call")
    assert result["allowed"] is True
    assert result["state"] == "closed"


def test_open_on_failures():
    svc = SandboxCircuitBreakerService()
    svc.register("sb-1", "api", failure_threshold=3)
    for _ in range(3):
        svc.record_failure("sb-1", "api")
    result = svc.can_execute("sb-1", "api")
    assert result["allowed"] is False
    assert result["state"] == "open"


def test_half_open_after_cooldown():
    svc = SandboxCircuitBreakerService()
    svc.register("sb-1", "api", failure_threshold=2, cooldown_seconds=0.01)
    svc.record_failure("sb-1", "api")
    svc.record_failure("sb-1", "api")
    time.sleep(0.02)
    result = svc.can_execute("sb-1", "api")
    assert result["allowed"] is True
    assert result["state"] == "half_open"


def test_half_open_to_closed():
    svc = SandboxCircuitBreakerService()
    svc.register("sb-1", "api", failure_threshold=1, success_threshold=2, cooldown_seconds=0.01)
    svc.record_failure("sb-1", "api")
    time.sleep(0.02)
    svc.can_execute("sb-1", "api")  # transitions to half_open
    svc.record_success("sb-1", "api")
    svc.record_success("sb-1", "api")
    status = svc.get_status("sb-1", "api")
    assert status["state"] == "closed"


def test_half_open_back_to_open():
    svc = SandboxCircuitBreakerService()
    svc.register("sb-1", "api", failure_threshold=1, cooldown_seconds=0.01)
    svc.record_failure("sb-1", "api")
    time.sleep(0.02)
    svc.can_execute("sb-1", "api")  # half_open
    state = svc.record_failure("sb-1", "api")
    assert state == CircuitState.OPEN


def test_force_open_close():
    svc = SandboxCircuitBreakerService()
    svc.register("sb-1", "api")
    svc.force_open("sb-1", "api")
    assert svc.can_execute("sb-1", "api")["allowed"] is False
    svc.force_close("sb-1", "api")
    assert svc.can_execute("sb-1", "api")["allowed"] is True


def test_failure_rate():
    svc = SandboxCircuitBreakerService()
    svc.register("sb-1", "api", failure_threshold=100)
    for _ in range(7):
        svc.record_success("sb-1", "api")
    for _ in range(3):
        svc.record_failure("sb-1", "api")
    status = svc.get_status("sb-1", "api")
    assert status["failure_rate"] == 30.0


def test_short_circuit_count():
    svc = SandboxCircuitBreakerService()
    svc.register("sb-1", "api", failure_threshold=1, cooldown_seconds=999)
    svc.record_failure("sb-1", "api")
    svc.can_execute("sb-1", "api")  # short-circuited
    svc.can_execute("sb-1", "api")
    status = svc.get_status("sb-1", "api")
    assert status["total_short_circuits"] == 2
