from app.services.app_marketplace_app_app_app_pricing_page import build_pricing_page

def test_pricing():
    r = build_pricing_page()
    assert r["tier_count"] == 3
    assert r["faq_count"] == 3
    pro = next(t for t in r["tiers"] if t["id"] == "pro")
    assert pro["recommended"]
    assert pro["price_display"] == "$29/mo"
    free = next(t for t in r["tiers"] if t["id"] == "free")
    assert free["price_display"] == "Free"
    ent = next(t for t in r["tiers"] if t["id"] == "enterprise")
    assert ent["price_display"] == "Custom"
