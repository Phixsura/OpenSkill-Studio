from app.services.app_marketplace_app_app_pricing_tier import get_plan, compare_plans, calculate_annual

def test_get_plan():
    r = get_plan(plan_id="pro")
    assert r["price"] == 29
    assert r["feature_count"] == 6

def test_unknown_plan():
    r = get_plan(plan_id="nonexistent")
    assert "error" in r

def test_compare():
    r = compare_plans()
    assert r["total"] == 4
    pro = next(p for p in r["plans"] if p["id"] == "pro")
    assert pro["recommended"]

def test_annual():
    r = calculate_annual(monthly_price=29, discount_pct=20)
    assert r["annual"] == 348
    assert r["savings"] == 69.6
