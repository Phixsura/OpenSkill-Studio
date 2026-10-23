from app.services.app_marketplace_app_pricing_tier_selector import get_pricing_tiers, recommend_tier

def test_tiers():
    r = get_pricing_tiers(annual_discount_pct=20)
    assert len(r["tiers"]) == 4
    pro = next(t for t in r["tiers"] if t["id"] == "pro")
    assert pro["highlighted"]
    assert pro["annual_price"] == round(99 * 12 * 0.8)

def test_recommend_free():
    r = recommend_tier(usage={"apps": 2, "api_calls_monthly": 500})
    assert r["recommended"] == "free"

def test_recommend_pro():
    r = recommend_tier(usage={"apps": 50, "api_calls_monthly": 100000})
    assert r["recommended"] == "pro"
