from app.services.app_marketplace_app_app_pricing_toggle import calculate_pricing

def test_pricing():
    r = calculate_pricing(monthly_price=29, annual_discount_pct=20)
    assert r["monthly"]["price"] == 29
    assert r["annual"]["price"] == 23.2
    assert r["savings"] == 69.6
    assert "Save $69.6" in r["savings_label"]

def test_no_discount():
    r = calculate_pricing(monthly_price=10, annual_discount_pct=0)
    assert r["annual"]["price"] == 10
    assert r["savings"] == 0
