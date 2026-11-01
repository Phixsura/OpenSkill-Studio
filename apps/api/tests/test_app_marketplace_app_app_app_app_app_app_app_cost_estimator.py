from app.services.app_marketplace_app_app_app_app_app_app_app_cost_estimator import estimate_cost, compare_plans

def test_estimate():
    r = estimate_cost("pro", {"api_calls": 100, "storage_gb": 50})
    assert r["base_price"] == 29.0
    assert r["variable_cost"] == 55.0  # 100*0.50 + 50*0.10
    assert r["total"] == 84.0

def test_compare():
    plans = compare_plans({"api_calls": 100})
    assert len(plans) == 3
    assert plans[0]["total"] == 0  # free
    assert plans[1]["total"] > plans[0]["total"]  # pro > free
