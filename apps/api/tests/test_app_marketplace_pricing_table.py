from app.services.app_marketplace_pricing_table import get_pricing_table, get_plan_recommendation, compute_annual_savings

def test_table():
    t = get_pricing_table()
    assert len(t) == 4
    pro = next(p for p in t if p["id"] == "pro")
    assert pro["highlighted"]
    assert pro["price_cents"] == 9900

def test_recommend_free():
    r = get_plan_recommendation(usage={"api_calls_per_day": 500, "app_count": 1, "team_size": 1})
    assert r["plan"] == "free"

def test_recommend_pro():
    r = get_plan_recommendation(usage={"api_calls_per_day": 100000, "app_count": 10})
    assert r["plan"] == "pro"

def test_annual():
    s = compute_annual_savings(monthly_price=9900)
    assert s["savings_pct"] > 0
    assert s["savings_cents"] > 0
