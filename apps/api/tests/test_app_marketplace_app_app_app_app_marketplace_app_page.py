from app.services.app_marketplace_app_app_app_app_marketplace_app_page import build_marketplace_app_page

def test_page():
    r = build_marketplace_app_page(
        app={"id": "a1", "name": "SuperApp", "icon": "🚀", "tagline": "Do more",
             "description": "Great", "version": "2.0.0", "pricing": "Free", "tags": ["tools"]},
        developer={"name": "Alice", "verified": True, "app_count": 5},
        stats={"installs": 25000, "avg_rating": 4.7, "review_count": 120},
        installed=False)
    assert r["app"]["name"] == "SuperApp"
    assert r["developer"]["verified"]
    assert r["stats"]["installs"] == 25000
    assert r["cta"] == "Install"

def test_installed():
    r = build_marketplace_app_page(app={"pricing": "Free"}, developer={}, stats={}, installed=True)
    assert r["cta"] == "Open"
