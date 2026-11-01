from app.services.app_marketplace_app_app_pricing_card_display import build_pricing_card

def test_free():
    plan = {"id": "free", "name": "Free", "price": 0, "features": ["5 apps", "1K calls"]}
    r = build_pricing_card(plan=plan)
    assert r["price_display"] == "Free"
    assert r["feature_count"] == 2

def test_paid():
    plan = {"id": "pro", "name": "Pro", "price": 99, "features": ["Unlimited", "Priority support"],
            "cta": "Start Trial", "popular": True}
    r = build_pricing_card(plan=plan, recommended=True)
    assert r["price_display"] == "$99"
    assert r["recommended"]
    assert r["popular"]
    assert r["cta"] == "Start Trial"

def test_custom():
    r = build_pricing_card(plan={"name": "Enterprise", "price": -1})
    assert r["price_display"] == "Custom"
