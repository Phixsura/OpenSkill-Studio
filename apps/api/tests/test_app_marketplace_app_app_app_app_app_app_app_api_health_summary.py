from app.services.app_marketplace_app_app_app_app_app_app_app_api_health_summary import summarize_api_health

def test_summary():
    eps = [
        {"path": "/users", "healthy": True, "latency_ms": 50, "error_rate": 0.1},
        {"path": "/apps", "healthy": True, "latency_ms": 80, "error_rate": 0.5},
        {"path": "/billing", "healthy": False, "latency_ms": 2000, "error_rate": 15.0},
    ]
    r = summarize_api_health(eps)
    assert r["healthy"] == 2
    assert r["overall"] == "critical"  # 67% < 80% threshold
    assert r["slowest"]["endpoint"] == "/billing"
    assert r["most_errors"]["endpoint"] == "/billing"
    assert r["health_pct"] == 67
