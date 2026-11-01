from app.services.app_marketplace_extension_circuit_breaker_reg import (
    CircuitBreakerRegService, CircuitState
)
import time


def test_starts_closed():
    svc = CircuitBreakerRegService()
    svc.register("/api/users", failure_threshold=3)
    ok, msg = svc.can_execute("/api/users")
    assert ok is True
    assert "closed" in msg


def test_opens_on_threshold():
    svc = CircuitBreakerRegService()
    svc.register("/api/data", failure_threshold=3)
    for _ in range(3):
        svc.can_execute("/api/data")
        svc.record_failure("/api/data")
    state = svc.record_failure("/api/data")
    ok, msg = svc.can_execute("/api/data")
    assert ok is False
    assert "circuit open" in msg


def test_half_open_after_timeout():
    svc = CircuitBreakerRegService()
    cb = svc.register("/api/slow", failure_threshold=2, recovery_timeout=0.01)
    svc.can_execute("/api/slow"); svc.record_failure("/api/slow")
    svc.can_execute("/api/slow"); svc.record_failure("/api/slow")
    # Now open — wait for recovery
    time.sleep(0.02)
    ok, msg = svc.can_execute("/api/slow")
    assert ok is True
    assert "half-open" in msg


def test_half_open_success_closes():
    svc = CircuitBreakerRegService()
    cb = svc.register("/api/recover", failure_threshold=2, success_threshold=2, recovery_timeout=0.01)
    svc.can_execute("/api/recover"); svc.record_failure("/api/recover")
    svc.can_execute("/api/recover"); svc.record_failure("/api/recover")
    time.sleep(0.02)
    svc.can_execute("/api/recover")  # enters half-open
    svc.record_success("/api/recover")
    svc.record_success("/api/recover")  # meets success_threshold
    assert cb.state == CircuitState.CLOSED


def test_half_open_failure_reopens():
    svc = CircuitBreakerRegService()
    cb = svc.register("/api/flaky", failure_threshold=2, recovery_timeout=0.01)
    svc.can_execute("/api/flaky"); svc.record_failure("/api/flaky")
    svc.can_execute("/api/flaky"); svc.record_failure("/api/flaky")
    time.sleep(0.02)
    svc.can_execute("/api/flaky")  # half-open
    svc.record_failure("/api/flaky")  # probe failed
    assert cb.state == CircuitState.OPEN


def test_success_resets_failure_count():
    svc = CircuitBreakerRegService()
    svc.register("/api/ok", failure_threshold=3)
    svc.can_execute("/api/ok"); svc.record_failure("/api/ok")
    svc.can_execute("/api/ok"); svc.record_failure("/api/ok")
    # 2 failures, 1 away from open
    svc.can_execute("/api/ok"); svc.record_success("/api/ok")
    # Success resets count
    cb = svc._breakers["/api/ok"]
    assert cb.failure_count == 0
    assert cb.state == CircuitState.CLOSED


def test_stats():
    svc = CircuitBreakerRegService()
    svc.register("/api/stats")
    for _ in range(10):
        svc.can_execute("/api/stats")
    for _ in range(3):
        svc.record_failure("/api/stats")
    stats = svc.get_stats("/api/stats")
    assert stats["total_requests"] == 10
    assert stats["total_failures"] == 3
    assert stats["failure_rate"] == 30.0


def test_short_circuit_counting():
    svc = CircuitBreakerRegService()
    cb = svc.register("/api/down", failure_threshold=1, recovery_timeout=999)
    svc.can_execute("/api/down"); svc.record_failure("/api/down")
    # Now open with long timeout
    svc.can_execute("/api/down")  # short-circuited
    svc.can_execute("/api/down")  # short-circuited
    assert cb.total_short_circuits == 2
