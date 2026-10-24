from app.services.app_marketplace_app_app_app_app_app_app_app_gw_circuit import GatewayCircuitBreaker

def test_circuit_lifecycle():
    cb = GatewayCircuitBreaker(failure_threshold=3, recovery_seconds=10)
    assert cb.can_pass("svc1")["allowed"]
    for _ in range(3):
        cb.record_failure("svc1", now=100.0)
    assert not cb.can_pass("svc1", now=105.0)["allowed"]
    # After recovery window
    r = cb.can_pass("svc1", now=111.0)
    assert r["allowed"]
    assert r["state"] == "half-open"

def test_success_resets():
    cb = GatewayCircuitBreaker(failure_threshold=2)
    cb.record_failure("svc1")
    cb.record_success("svc1")
    assert cb.can_pass("svc1")["state"] == "closed"
    assert cb.summary()["open"] == 0
