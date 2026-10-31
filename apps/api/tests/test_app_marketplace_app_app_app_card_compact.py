from app.services.app_marketplace_app_app_app_card_compact import build_compact_card, build_card_list

def test_card():
    r = build_compact_card(app={"id": "a1", "name": "Auth SDK", "developer": "Alice",
        "rating": 4.7, "installs": 5200, "price": 0, "category": "security"})
    assert r["name"] == "Auth SDK"
    assert r["icon_letter"] == "A"
    assert r["install_display"] == "5K+"
    assert r["price_label"] == "Free"
    assert "★★★★★" in r["stars_display"]

def test_paid():
    r = build_compact_card(app={"name": "Pro Tool", "price": 9.99, "installs": 500})
    assert r["price_label"] == "$9.99"
    assert r["install_display"] == "500"

def test_list():
    r = build_card_list(apps=[{"name": "A"}, {"name": "B"}])
    assert r["total"] == 2
