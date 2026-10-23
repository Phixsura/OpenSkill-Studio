from app.services.app_marketplace_app_app_app_app_app_app_app_endpoint_health import check_endpoints

def test_endpoints():
    eps = [
        {"path": "/api/v1/users", "method": "GET", "status_code": 200, "latency_ms": 45},
        {"path": "/api/v1/apps", "method": "GET", "status_code": 200, "latency_ms": 120},
        {"path": "/api/v1/billing", "method": "POST", "status_code": 500, "latency_ms": 3000},
    ]
    r = check_endpoints(eps)
    assert r["healthy"] == 2
    assert r["unhealthy"] == 1
    assert r["overall"] == "degraded"
    assert r["results"][0]["path"] == "/api/v1/billing"  # slowest first
    assert r["health_pct"] == 67
