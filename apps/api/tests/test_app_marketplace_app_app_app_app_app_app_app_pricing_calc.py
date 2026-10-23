from app.services.app_marketplace_app_app_app_app_app_app_app_pricing_calc import calculate_pricing, compare_plans

def test_pricing():
    r = calculate_pricing(base_price=29, usage_units=10000, price_per_unit=0.001, discount_pct=10)
    assert r["base_price"] == 29
    assert r["usage_cost"] == 10.0
    assert r["subtotal"] == 39.0
    assert r["discount"] == 3.9
    assert r["total"] == 35.1

def test_compare():
    r = compare_plans([
        {"base_price": 29, "usage_units": 0, "price_per_unit": 0},
        {"base_price": 99, "usage_units": 0, "price_per_unit": 0},
    ])
    assert r["plan_count"] == 2
    assert r["cheapest_annual"] == 29 * 12
