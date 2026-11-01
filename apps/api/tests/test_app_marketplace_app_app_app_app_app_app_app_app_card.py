from app.services.app_marketplace_app_app_app_app_app_app_app_app_card import build_app_card, build_card_grid

def test_card():
    c = build_app_card({"name": "Slack Bot", "description": "Connect with Slack",
                         "rating": 4.5, "installs": 50000, "verified": True,
                         "price_type": "free", "developer": "Acme", "category": "communication"})
    assert c["name"] == "Slack Bot"
    assert c["install_display"] == "50,000"
    assert c["verified"]
    assert c["price_display"] == "Free"

def test_grid():
    apps = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
    r = build_card_grid(apps)
    assert r["total"] == 3
