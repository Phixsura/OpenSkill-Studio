from app.services.app_marketplace_pricing_plan import create_pricing_plan, compare_plans, calculate_savings

def test_create():
    p = create_pricing_plan(app_id="a1", name="Pro", price_cents=999, interval="monthly", features=["api", "webhooks"])
    assert not p["is_free"]
    assert p["price_cents"] == 999

def test_free():
    p = create_pricing_plan(app_id="a1", name="Free", price_cents=0, interval="monthly", features=["basic"])
    assert p["is_free"]

def test_invalid_interval():
    p = create_pricing_plan(app_id="a1", name="X", price_cents=100, interval="weekly", features=[])
    assert p["error"]

def test_compare():
    plans = [{"name": "Free", "price_cents": 0, "features": ["basic"]},
             {"name": "Pro", "price_cents": 999, "features": ["basic", "api"]}]
    c = compare_plans(plans=plans)
    assert len(c["matrix"]) == 2

def test_savings():
    s = calculate_savings(monthly_price=999, yearly_price=9990)
    assert s["savings_pct"] == 17
    assert s["savings_cents"] == 1998
