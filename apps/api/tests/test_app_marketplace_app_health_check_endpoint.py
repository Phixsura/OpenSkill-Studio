from app.services.app_marketplace_app_health_check_endpoint import build_health_check_config, evaluate_health_result, compute_availability

def test_config():
    c = build_health_check_config(app_id="a1", endpoint="/health")
    assert c["status"] == "active"

def test_config_too_fast():
    c = build_health_check_config(app_id="a1", endpoint="/health", interval_seconds=5)
    assert c["error"]

def test_healthy():
    r = evaluate_health_result(status_code=200, response_time_ms=100, expected_status=200, timeout_ms=5000)
    assert r["healthy"]

def test_unhealthy_status():
    r = evaluate_health_result(status_code=500, response_time_ms=100, expected_status=200, timeout_ms=5000)
    assert not r["healthy"]
    assert "Wrong status code" in r["issues"]

def test_availability():
    results = [{"healthy": True}] * 95 + [{"healthy": False}] * 5
    a = compute_availability(results=results)
    assert a["availability_pct"] == 95.0
