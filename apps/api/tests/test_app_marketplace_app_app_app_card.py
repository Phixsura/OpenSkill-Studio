from app.services.app_marketplace_app_app_app_card import build_app_card, build_app_grid

def test_card():
    r = build_app_card(app={"id": "a1", "name": "SuperApp", "description": "A great productivity tool",
                             "icon": "🚀", "rating": 4.5, "downloads": 25000, "category": "productivity",
                             "verified": True, "pricing": "$9/mo"})
    assert r["name"] == "SuperApp"
    assert r["downloads_display"] == "25.0K"
    assert r["verified"]
    assert "★" in r["stars"]

def test_grid():
    apps = [{"id": "1", "name": "A", "category": "tools"}, {"id": "2", "name": "B", "category": "games"}]
    r = build_app_grid(apps=apps)
    assert r["total"] == 2
    assert "games" in r["categories"]
