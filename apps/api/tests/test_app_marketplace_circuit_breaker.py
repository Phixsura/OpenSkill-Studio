from app.services.app_marketplace_circuit_breaker import (
    CircuitBreaker, CircuitState,
)


def test_closed_by_default():
    cb = CircuitBreaker()
    allowed, state = cb.allow_request("ext-1")
    assert allowed is True
    assert state == CircuitState.CLOSED


def test_opens_after_threshold():
    cb = CircuitBreaker(failure_threshold=3)
    for _ in range(3):
        cb.record_failure("ext-2")
    allowed, state = cb.allow_request("ext-2")
    assert allowed is False
    assert state == CircuitState.OPEN


def test_success_resets_consecutive():
    cb = CircuitBreaker(failure_threshold=3)
    cb.record_failure("ext-3")
    cb.record_failure("ext-3")
    cb.record_success("ext-3")  # resets consecutive
    cb.record_failure("ext-3")
    allowed, _ = cb.allow_request("ext-3")
    assert allowed is True  # only 1 consecutive, not 3


def test_half_open_recovery():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.0)
    cb.record_failure("ext-4")
    cb.record_failure("ext-4")
    # Should be open, but recovery_timeout=0 → immediately half-open
    allowed, state = cb.allow_request("ext-4")
    assert allowed is True
    assert state == CircuitState.HALF_OPEN
    cb.record_success("ext-4")
    assert cb.get_state("ext-4") == CircuitState.CLOSED


def test_half_open_failure_reopens():
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.0)
    cb.record_failure("ext-5")
    cb.allow_request("ext-5")  # half-open
    new_state = cb.record_failure("ext-5")
    assert new_state == CircuitState.OPEN


def test_stats():
    cb = CircuitBreaker()
    cb.record_success("ext-6")
    cb.record_success("ext-6")
    cb.record_failure("ext-6")
    stats = cb.get_stats("ext-6")
    assert stats["successes"] == 2
    assert stats["failures"] == 1


def test_reset():
    cb = CircuitBreaker(failure_threshold=1)
    cb.record_failure("ext-7")
    cb.reset("ext-7")
    allowed, _ = cb.allow_request("ext-7")
    assert allowed is True
