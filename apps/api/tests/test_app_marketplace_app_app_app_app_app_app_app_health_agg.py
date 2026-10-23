from app.services.app_marketplace_app_app_app_app_app_app_app_health_agg import aggregate_health

def test_all_healthy():
    r = aggregate_health([
        {"service": "api", "status": "healthy", "latency_ms": 50},
        {"service": "db", "status": "healthy", "latency_ms": 10},
    ])
    assert r["overall"] == "healthy"
    assert r["health_pct"] == 100

def test_degraded():
    r = aggregate_health([
        {"service": "api", "status": "healthy", "latency_ms": 50},
        {"service": "db", "status": "unhealthy", "latency_ms": 10},
    ])
    assert r["overall"] == "degraded"
    assert r["healthy"] == 1
