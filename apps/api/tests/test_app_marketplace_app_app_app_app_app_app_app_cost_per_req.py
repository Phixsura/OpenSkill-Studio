from app.services.app_marketplace_app_app_app_app_app_app_app_cost_per_req import calculate_cost_per_request, cost_by_endpoint

def test_cost():
    r = calculate_cost_per_request(1000, 10000000)
    assert r["cost_per_1k_requests"] == 0.1
    assert r["cost_per_million"] == 100

def test_by_endpoint():
    r = cost_by_endpoint([
        {"endpoint": "/users", "requests": 7000},
        {"endpoint": "/orders", "requests": 3000},
    ], total_cost=100)
    assert r[0]["endpoint"] == "/users"
    assert r[0]["share_pct"] == 70.0
    assert r[0]["cost"] == 70
