from app.services.app_marketplace_app_app_app_app_app_app_app_circuit_breaker import CircuitBreaker

def test_circuit_breaker():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=10)
    assert cb.call(now=0)["allowed"]
    cb.record_failure(now=1)
    cb.record_failure(now=2)
    assert cb.status()["state"] == "closed"
    cb.record_failure(now=3)
    assert cb.status()["state"] == "open"
    r = cb.call(now=5)
    assert not r["allowed"]
    assert r["state"] == "open"
    # After recovery timeout
    r2 = cb.call(now=14)
    assert r2["allowed"]
    assert r2["state"] == "half_open"
    cb.record_success()
    assert cb.status()["state"] == "closed"
