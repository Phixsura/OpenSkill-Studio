from app.services.app_marketplace_app_app_app_app_app_app_app_app_health_ind import compute_app_health

def test_healthy():
    r = compute_app_health(error_rate=0.1, avg_latency_ms=85, uptime_pct=99.99, user_satisfaction=4.8)
    assert r["grade"] == "A"
    assert r["score"] == 100

def test_degraded():
    r = compute_app_health(error_rate=3.0, avg_latency_ms=600, uptime_pct=98.5, user_satisfaction=3.5)
    assert r["grade"] in ("C", "D")
    assert r["score"] < 50
