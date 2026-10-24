from app.services.app_marketplace_app_app_app_app_app_app_app_gw_observ import gateway_metrics

def test_metrics():
    r = gateway_metrics([
        {"route": "/api/users", "status": 200, "latency_ms": 50},
        {"route": "/api/users", "status": 200, "latency_ms": 60},
        {"route": "/api/orders", "status": 500, "latency_ms": 200},
        {"route": "/api/users", "status": 404, "latency_ms": 10},
    ])
    assert r["total"] == 4
    assert r["error_rate_pct"] == 25.0
    assert r["top_routes"][0]["route"] == "/api/users"
    assert r["by_status"]["2xx"] == 2
