from app.services.app_marketplace_app_app_app_app_app_app_app_health_agg import aggregate_health, health_history

def test_healthy():
    r = aggregate_health([
        {"name": "api", "status": "up", "latency_ms": 10},
        {"name": "db", "status": "up", "latency_ms": 5},
    ])
    assert r["overall"] == "healthy"
    assert r["uptime_pct"] == 100.0

def test_degraded():
    r = aggregate_health([
        {"name": "api", "status": "up", "latency_ms": 10},
        {"name": "db", "status": "down", "latency_ms": 0},
        {"name": "cache", "status": "up", "latency_ms": 2},
    ])
    assert r["overall"] == "degraded"

def test_history():
    r = health_history([
        {"uptime_pct": 95.0}, {"uptime_pct": 99.0},
    ])
    assert r["trend"] == "improving"
