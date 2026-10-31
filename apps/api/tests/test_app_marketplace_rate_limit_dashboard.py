from app.services.app_marketplace_rate_limit_dashboard import compute_rate_limit_usage, get_rate_limited_requests, suggest_limit_adjustments

def test_usage():
    endpoints = [{"path": "/users", "limit": 100, "current": 80}, {"path": "/apps", "limit": 200, "current": 50}]
    r = compute_rate_limit_usage(endpoints=endpoints)
    assert r["usage_pct"] > 40
    assert r["hotspot_count"] == 1

def test_limited():
    requests = [{"status_code": 200, "path": "/a"}] * 95 + [{"status_code": 429, "path": "/a"}] * 5
    r = get_rate_limited_requests(requests=requests)
    assert r["total_limited"] == 5
    assert r["rate"] == 5.0

def test_suggestions():
    hotspots = [{"path": "/users", "limit": 100, "current": 98}]
    s = suggest_limit_adjustments(usage={}, hotspots=hotspots)
    assert len(s) == 1
    assert s[0]["suggested_limit"] == 200
