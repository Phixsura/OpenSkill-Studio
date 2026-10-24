from app.services.app_marketplace_api_rate_limit_dashboard import get_rate_limit_status

def test_healthy():
    eps = [{"path": "/api/v1/apps", "limit": 1000, "used": 200, "reset_in_sec": 60}]
    r = get_rate_limit_status(endpoints=eps)
    assert r["overall_health"] == "healthy"
    assert r["endpoints"][0]["usage_pct"] == 20.0

def test_throttled():
    eps = [{"path": "/api/v1/search", "limit": 100, "used": 120}]
    r = get_rate_limit_status(endpoints=eps)
    assert r["throttled_count"] == 1
    assert r["overall_health"] == "critical"
    assert r["endpoints"][0]["throttled"]

def test_warning():
    eps = [{"path": "/api/v1/apps", "limit": 100, "used": 85}]
    r = get_rate_limit_status(endpoints=eps)
    assert r["endpoints"][0]["warning"]
    assert not r["endpoints"][0]["throttled"]
