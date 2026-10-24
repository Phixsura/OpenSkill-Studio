from app.services.app_marketplace_app_circuit_breaker_dashboard import get_circuit_status, build_circuit_dashboard, should_allow_request

def test_closed():
    s = get_circuit_status(failure_count=2, threshold=5, last_failure_ago_seconds=10)
    assert s["state"] == "closed"

def test_open():
    s = get_circuit_status(failure_count=5, threshold=5, last_failure_ago_seconds=10)
    assert s["state"] == "open"

def test_half_open():
    s = get_circuit_status(failure_count=5, threshold=5, last_failure_ago_seconds=60, recovery_timeout=30)
    assert s["state"] == "half_open"

def test_dashboard():
    circuits = [{"name": "api", "state": "closed"}, {"name": "webhook", "state": "open"}]
    d = build_circuit_dashboard(circuits=circuits)
    assert d["health"] == "degraded"
    assert d["by_state"]["open"] == 1

def test_allow():
    assert should_allow_request(circuit={"state": "closed"})
    assert not should_allow_request(circuit={"state": "open"})
