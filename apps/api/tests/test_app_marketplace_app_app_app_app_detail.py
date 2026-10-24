from app.services.app_marketplace_app_app_app_app_detail import build_app_detail

def test_detail():
    app = {"name": "SuperApp", "icon": "🚀", "version": "2.0.0", "author": "Alice",
           "verified": True, "tagline": "Do more", "description": "A great app",
           "installs": 25000, "rating": 4.5, "pricing": "Free", "tags": ["tools"]}
    reviews = [{"rating": 5}, {"rating": 4}]
    similar = [{"id": "s1", "name": "Similar", "icon": "📦"}]
    r = build_app_detail(app=app, reviews=reviews, similar=similar, installed=False)
    assert r["header"]["name"] == "SuperApp"
    assert r["stats"]["review_count"] == 2
    assert r["cta"] == "Install"
    assert r["has_similar"]

def test_installed():
    r = build_app_detail(app={"name": "X", "pricing": "Free"}, installed=True)
    assert r["cta"] == "Open"
