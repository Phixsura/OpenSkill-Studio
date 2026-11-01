from app.services.app_marketplace_app_app_app_app_app_app_app_healthcheck_agg import aggregate_health, format_status_page

def test_health():
    checks = [
        {"name": "API", "status": "healthy", "latency_ms": 25},
        {"name": "Database", "status": "healthy", "latency_ms": 5},
        {"name": "Cache", "status": "unhealthy", "latency_ms": 0, "message": "Connection refused"},
    ]
    r = aggregate_health(checks)
    assert r["overall"] == "degraded"
    assert r["healthy"] == 2
    assert r["health_pct"] == 67
    assert len(r["issues"]) == 1

def test_status_page():
    h = aggregate_health([{"name": "API", "status": "healthy", "latency_ms": 10}])
    sp = format_status_page(h)
    assert "HEALTHY" in sp["text"]
    assert "API" in sp["text"]
