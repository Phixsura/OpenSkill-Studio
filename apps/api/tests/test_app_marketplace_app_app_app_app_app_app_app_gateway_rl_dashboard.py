from app.services.app_marketplace_app_app_app_app_app_app_app_gateway_rl_dashboard import aggregate_rate_limits

def test_aggregate():
    routes = [
        {"path": "/api/v1/users", "method": "GET", "requests": 950, "blocked": 50, "limit": 1000},
        {"path": "/api/v1/apps", "method": "GET", "requests": 200, "blocked": 0, "limit": 500},
        {"path": "/api/v1/search", "method": "POST", "requests": 80, "blocked": 0, "limit": 100},
    ]
    r = aggregate_rate_limits(routes)
    assert r["total_requests"] == 1230
    assert r["total_blocked"] == 50
    assert r["exceeded_count"] == 1
    assert r["routes"][0]["path"] == "/api/v1/users"  # highest usage
    assert r["block_rate"] > 0
