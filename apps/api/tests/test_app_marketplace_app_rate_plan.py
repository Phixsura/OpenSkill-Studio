from app.services.app_marketplace_app_rate_plan import calculate_usage_cost, compare_plans

def test_usage_cost():
    plan = {"base_fee": 10, "dimensions": [
        {"key": "api_calls", "label": "API Calls", "unit_price": 0.001, "free_tier": 1000}]}
    usage = {"api_calls": 5000}
    r = calculate_usage_cost(plan=plan, usage=usage)
    assert r["subtotal"] == 14.0  # 10 base + 4000 * 0.001
    assert len(r["line_items"]) == 2

def test_free_tier():
    plan = {"dimensions": [{"key": "calls", "label": "Calls", "unit_price": 0.01, "free_tier": 1000}]}
    usage = {"calls": 500}
    r = calculate_usage_cost(plan=plan, usage=usage)
    assert r["subtotal"] == 0  # under free tier

def test_compare():
    plans = [
        {"name": "Starter", "base_fee": 0, "dimensions": [{"key": "calls", "label": "Calls", "unit_price": 0.01, "free_tier": 0}]},
        {"name": "Pro", "base_fee": 20, "dimensions": [{"key": "calls", "label": "Calls", "unit_price": 0.005, "free_tier": 1000}]},
    ]
    usage = {"calls": 5000}
    r = compare_plans(plans=plans, usage=usage)
    assert r["recommended"] == "Pro"  # 20 + 4000*0.005=40 vs 5000*0.01=50
