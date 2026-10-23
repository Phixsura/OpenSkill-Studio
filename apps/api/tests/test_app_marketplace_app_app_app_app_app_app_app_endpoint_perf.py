from app.services.app_marketplace_app_app_app_app_app_app_app_endpoint_perf import track_performance

def test_perf():
    requests = [
        {"method": "GET", "path": "/users", "latency_ms": 50, "status_code": 200},
        {"method": "GET", "path": "/users", "latency_ms": 45, "status_code": 200},
        {"method": "GET", "path": "/users", "latency_ms": 200, "status_code": 500},
        {"method": "POST", "path": "/apps", "latency_ms": 120, "status_code": 201},
    ]
    r = track_performance(requests)
    assert r["total_endpoints"] == 2
    assert r["total_requests"] == 4
    users = next(e for e in r["endpoints"] if "users" in e["endpoint"])
    assert users["total"] == 3
    assert users["errors"] == 1
    assert users["error_rate"] > 0
