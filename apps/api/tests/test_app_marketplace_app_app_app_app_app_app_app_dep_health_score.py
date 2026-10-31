from app.services.app_marketplace_app_app_app_app_app_app_app_dep_health_score import calculate_dep_health

def test_healthy():
    r = calculate_dep_health([
        {"name": "db", "latency_ms": 5, "error_rate_pct": 0.1, "availability_pct": 99.99},
        {"name": "cache", "latency_ms": 1, "error_rate_pct": 0, "availability_pct": 100},
    ])
    assert r["status"] == "healthy"
    assert r["score"] > 90

def test_critical():
    r = calculate_dep_health([
        {"name": "db", "latency_ms": 2000, "error_rate_pct": 20, "availability_pct": 80},
    ])
    assert r["status"] == "critical"
    assert r["weakest"] == "db"
