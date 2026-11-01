from app.services.app_marketplace_app_app_app_app_app_app_app_circuit_breaker import (
    create_breaker, record_result, get_status, clear_breakers,
)

def test_trip():
    clear_breakers()
    create_breaker("db", failure_threshold=3)
    record_result("db", False)
    record_result("db", False)
    r = record_result("db", False)  # 3rd failure
    assert r["state"] == "open"
    assert not r["allowed"]
    s = get_status("db")
    assert s["total_trips"] == 1
    clear_breakers()

def test_recovery():
    clear_breakers()
    create_breaker("api", failure_threshold=2, recovery_sec=0)  # instant recovery
    record_result("api", False)
    record_result("api", False)  # trips open
    r = record_result("api", True)  # recovery_sec=0 → half_open, success → closed
    assert r["state"] == "closed"
    clear_breakers()
