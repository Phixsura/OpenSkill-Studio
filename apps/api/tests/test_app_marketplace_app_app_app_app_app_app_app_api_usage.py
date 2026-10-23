from app.services.app_marketplace_app_app_app_app_app_app_app_api_usage import analyze_usage

def test_usage():
    requests = [
        {"method": "GET", "path": "/users", "status": 200, "latency_ms": 50},
        {"method": "GET", "path": "/users", "status": 200, "latency_ms": 60},
        {"method": "POST", "path": "/users", "status": 201, "latency_ms": 100},
        {"method": "GET", "path": "/health", "status": 500, "latency_ms": 200},
    ]
    r = analyze_usage(requests)
    assert r["total_requests"] == 4
    assert r["error_count"] == 1
    assert r["error_rate_pct"] == 25.0
    assert r["top_endpoint"] == "GET /users"
    assert r["avg_latency_ms"] == 102
