from app.services.app_marketplace_app_app_circuit_breaker import CircuitBreaker

def test_closed():
    cb = CircuitBreaker(failure_threshold=3)
    assert cb.can_execute()["allowed"]
    assert cb.state == "closed"

def test_opens_after_threshold():
    cb = CircuitBreaker(failure_threshold=3)
    for _ in range(3):
        cb.record_failure(now=0)
    assert cb.state == "open"
    assert not cb.can_execute(now=0)["allowed"]

def test_half_open_recovery():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_s=10)
    cb.record_failure(now=0)
    cb.record_failure(now=1)
    assert cb.state == "open"
    r = cb.can_execute(now=12)
    assert r["allowed"]
    assert r["state"] == "half_open"

def test_close_on_success():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_s=5)
    cb.record_failure(now=0)
    cb.record_failure(now=0)
    cb.can_execute(now=10)  # transitions to half_open
    cb.record_success()
    assert cb.state == "closed"
