from app.services.app_marketplace_app_app_app_app_app_app_app_ep_cost import analyze_endpoint_cost, identify_expensive

def test_analyze():
    r = analyze_endpoint_cost([
        {"endpoint": "/users", "compute_units": 70, "requests": 10000},
        {"endpoint": "/reports", "compute_units": 30, "requests": 100},
    ], total_infra_cost=1000)
    assert r["endpoints"][0]["endpoint"] == "/users"
    assert r["endpoints"][0]["cost"] == 700

def test_expensive():
    r = identify_expensive([
        {"endpoint": "/a", "cost_per_1k": 0.5},
        {"endpoint": "/b", "cost_per_1k": 5.0},
    ], threshold_per_1k=1.0)
    assert len(r) == 1
    assert r[0]["endpoint"] == "/b"
