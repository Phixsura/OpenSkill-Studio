from app.services.app_marketplace_app_bundle_pricing import create_bundle, calculate_tier_pricing

def test_bundle():
    apps = [{"id": "a1", "name": "App A", "price": 10.0},
            {"id": "a2", "name": "App B", "price": 20.0}]
    r = create_bundle(name="Starter Pack", apps=apps, discount_pct=25)
    assert r["individual_total"] == 30.0
    assert r["bundle_price"] == 22.5
    assert r["savings"] == 7.5

def test_too_few():
    r = create_bundle(name="X", apps=[{"id": "a1", "name": "A"}])
    assert "error" in r

def test_tiers():
    tiers = [
        {"name": "Basic", "multiplier": 1.0, "features": ["core"]},
        {"name": "Pro", "multiplier": 2.5, "features": ["core", "analytics"], "recommended": True},
    ]
    r = calculate_tier_pricing(base_price=9.99, tiers=tiers)
    assert r["tiers"][0]["price"] == 9.99
    assert r["tiers"][1]["price"] == 24.98
    assert r["tiers"][1]["recommended"]
