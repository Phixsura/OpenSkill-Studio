from app.services.app_marketplace_app_app_api_rate_dashboard import build_rate_dashboard

def test_dashboard():
    endpoints = [
        {"path": "/api/apps", "method": "GET", "current_rpm": 80, "rpm_limit": 100},
        {"path": "/api/users", "method": "GET", "current_rpm": 150, "rpm_limit": 100},
    ]
    r = build_rate_dashboard(endpoints=endpoints)
    assert r["total_endpoints"] == 2
    assert r["throttled_count"] == 1
    assert not r["healthy"]
    assert r["endpoints"][0]["path"] == "/api/users"  # sorted by usage

def test_healthy():
    r = build_rate_dashboard(endpoints=[{"path": "/api/x", "current_rpm": 10, "rpm_limit": 100}])
    assert r["healthy"]
