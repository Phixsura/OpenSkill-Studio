from app.services.app_marketplace_app_app_app_app_app_app_app_traffic_analyze import analyze_traffic

def test_analyze():
    r = analyze_traffic([
        {"method": "GET", "path": "/api/users", "status": 200, "latency_ms": 50},
        {"method": "GET", "path": "/api/users", "status": 200, "latency_ms": 60},
        {"method": "POST", "path": "/api/orders", "status": 201, "latency_ms": 100},
        {"method": "GET", "path": "/api/users", "status": 500, "latency_ms": 200},
    ])
    assert r["total_requests"] == 4
    assert r["top_path"] == "/api/users"
    assert r["error_count"] == 1
    assert r["error_pct"] == 25.0
