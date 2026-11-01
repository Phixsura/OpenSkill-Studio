from app.services.app_marketplace_app_app_app_app_api_status import build_api_status

def test_all_healthy():
    services = [
        {"name": "API Gateway", "status": "healthy", "uptime_pct": 99.99, "avg_latency_ms": 45},
        {"name": "Auth Service", "status": "healthy", "uptime_pct": 99.95, "avg_latency_ms": 30},
    ]
    r = build_api_status(services=services)
    assert r["overall"] == "operational"
    assert r["healthy"] == 2
    assert r["avg_latency_ms"] == 38  # (45+30)/2 rounded

def test_degraded():
    services = [{"name": "API", "status": "healthy"}, {"name": "DB", "status": "degraded"}]
    r = build_api_status(services=services)
    assert r["overall"] == "degraded"
