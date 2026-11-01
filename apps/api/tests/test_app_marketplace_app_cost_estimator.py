from app.services.app_marketplace_app_cost_estimator import estimate_monthly_cost, compare_plans_cost, get_cost_optimization_tips

def test_estimate():
    r = estimate_monthly_cost(api_calls=50000, storage_gb=10, bandwidth_gb=20, sandbox_hours=100)
    assert r["total_usd"] > 0
    assert r["breakdown"]["api"] == 40.0  # (50000-10000) * 0.001

def test_free_tier():
    r = estimate_monthly_cost(api_calls=5000, storage_gb=0, bandwidth_gb=0, sandbox_hours=0)
    assert r["total_usd"] == 0

def test_compare():
    plans = [
        {"name": "Free", "base_price": 0, "included": {"api_calls": 1000}, "overage_rates": {"api_calls": 0.002}},
        {"name": "Pro", "base_price": 29, "included": {"api_calls": 100000}, "overage_rates": {"api_calls": 0.001}},
    ]
    r = compare_plans_cost(usage={"api_calls": 50000}, plans=plans)
    assert r[0]["plan"] == "Pro"  # cheaper with high usage

def test_tips_high():
    tips = get_cost_optimization_tips(breakdown={"api": 50, "storage": 10, "bandwidth": 8, "compute": 15})
    assert len(tips) == 4

def test_tips_low():
    tips = get_cost_optimization_tips(breakdown={"api": 1, "storage": 0.5})
    assert "optimized" in tips[0]
