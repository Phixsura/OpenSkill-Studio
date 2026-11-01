from app.services.app_marketplace_app_app_rate_limit_dashboard import build_rate_limit_dashboard

def test_healthy():
    eps = [{"method": "GET", "path": "/api/apps", "current_rpm": 500, "rpm_limit": 1000}]
    r = build_rate_limit_dashboard(endpoints=eps)
    assert r["healthy"]
    assert r["throttled_count"] == 0
    assert r["total_rpm"] == 500

def test_throttled():
    eps = [{"method": "GET", "path": "/api/apps", "current_rpm": 1200, "rpm_limit": 1000}]
    r = build_rate_limit_dashboard(endpoints=eps)
    assert not r["healthy"]
    assert r["throttled_count"] == 1
