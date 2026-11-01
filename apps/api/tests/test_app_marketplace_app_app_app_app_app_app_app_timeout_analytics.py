from app.services.app_marketplace_app_app_app_app_app_app_app_timeout_analytics import analyze_timeouts

def test_timeouts():
    reqs = [{"endpoint": "/api/fast", "duration_ms": 100}] * 100
    reqs += [{"endpoint": "/api/slow", "duration_ms": 6000}] * 10
    reqs += [{"endpoint": "/api/slow", "duration_ms": 100}] * 90
    r = analyze_timeouts(reqs, timeout_ms=5000)
    assert r["total_timeouts"] == 10
    assert r["endpoints"][0]["endpoint"] == "/api/slow"
    assert r["endpoints"][0]["timeout_rate"] == 10.0
