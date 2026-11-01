from app.services.app_marketplace_app_health_check import run_health_checks, get_uptime_history

def test_all_healthy():
    eps = [{"url": "/health", "status_code": 200, "latency_ms": 30},
           {"url": "/api", "status_code": 200, "latency_ms": 80}]
    r = run_health_checks(app_id="a1", endpoints=eps)
    assert r["all_healthy"]
    assert r["healthy_count"] == 2
    assert r["avg_latency_ms"] == 55.0

def test_unhealthy():
    eps = [{"url": "/health", "status_code": 503, "latency_ms": 100}]
    r = run_health_checks(app_id="a1", endpoints=eps)
    assert not r["all_healthy"]

def test_uptime():
    r = get_uptime_history(app_id="a1", days=30)
    assert r["overall_uptime"] > 99.0
    assert len(r["daily"]) == 30
