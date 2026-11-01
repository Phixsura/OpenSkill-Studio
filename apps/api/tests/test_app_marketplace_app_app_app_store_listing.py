from app.services.app_marketplace_app_app_app_store_listing import build_store_listing

def test_listing():
    app = {
        "name": "SuperApp", "description": "An amazing productivity app for teams",
        "icon": "🚀", "category": "Productivity", "version": "2.1.0",
        "author": "Alice", "downloads": 15000, "pricing": "$9/mo",
        "tags": ["productivity", "teams"], "verified": True,
        "screenshots": ["s1.png", "s2.png"],
        "reviews": [{"rating": 5}, {"rating": 4}, {"rating": 5}],
    }
    r = build_store_listing(app=app)
    assert r["name"] == "SuperApp"
    assert r["avg_rating"] == 4.7
    assert r["review_count"] == 3
    assert r["screenshot_count"] == 2
    assert r["verified"]
    assert "★" in r["stars_display"]

def test_empty_reviews():
    r = build_store_listing(app={"name": "Basic"})
    assert r["avg_rating"] == 0
    assert r["pricing"] == "Free"
