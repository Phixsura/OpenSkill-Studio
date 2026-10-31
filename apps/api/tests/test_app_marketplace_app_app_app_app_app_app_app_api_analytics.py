from app.services.app_marketplace_app_app_app_app_app_app_app_api_analytics import analyze_endpoints, peak_hours

def test_analyze():
    r = analyze_endpoints([
        {"endpoint": "/users", "method": "GET", "status": 200, "latency_ms": 50},
        {"endpoint": "/users", "method": "GET", "status": 200, "latency_ms": 60},
        {"endpoint": "/orders", "method": "POST", "status": 500, "latency_ms": 200},
    ])
    assert r["total_requests"] == 3
    assert r["by_method"]["GET"] == 2
    assert r["unique_endpoints"] == 2

def test_peak():
    r = peak_hours([{"hour": 9}, {"hour": 9}, {"hour": 14}, {"hour": 9}])
    assert r["peak_hour"] == 9
    assert r["peak_count"] == 3
