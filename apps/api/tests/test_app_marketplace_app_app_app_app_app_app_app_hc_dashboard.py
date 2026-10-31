from app.services.app_marketplace_app_app_app_app_app_app_app_hc_dashboard import build_dashboard

def test_dashboard():
    r = build_dashboard([
        {"name": "api", "category": "services", "status": "healthy", "latency_ms": 5},
        {"name": "db", "category": "infrastructure", "status": "healthy", "latency_ms": 2},
        {"name": "cache", "category": "infrastructure", "status": "degraded", "latency_ms": 50},
        {"name": "queue", "category": "services", "status": "healthy", "latency_ms": 3},
    ])
    assert not r["all_healthy"]
    assert r["health_pct"] == 75.0
    assert r["categories"]["services"]["all_healthy"]
    assert not r["categories"]["infrastructure"]["all_healthy"]
