from app.services.app_marketplace_app_app_app_app_app_app_app_cost_per_req import calculate_cost_per_request, compare_cost_efficiency

def test_calculate():
    r = calculate_cost_per_request(5000, 10_000_000)
    assert r["cost_per_1k"] == 0.5
    assert r["cost_per_million"] == 500.0

def test_compare():
    c = calculate_cost_per_request(4000, 10_000_000)
    p = calculate_cost_per_request(5000, 10_000_000)
    r = compare_cost_efficiency(c, p)
    assert r["improving"]
    assert r["delta"] < 0
