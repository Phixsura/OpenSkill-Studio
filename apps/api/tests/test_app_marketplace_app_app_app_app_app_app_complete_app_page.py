from app.services.app_marketplace_app_app_app_app_app_app_complete_app_page import build_complete_app_page

def test_page():
    r = build_complete_app_page(
        app={"id": "a1", "name": "SuperApp", "icon": "🚀", "tagline": "Do more",
             "description": "Great", "pricing": "Free", "tags": ["tools"]},
        developer={"name": "Alice", "verified": True, "app_count": 5},
        stats={"installs": 25000, "avg_rating": 4.7, "api_calls": 100000},
        reviews=[{"rating": 5, "title": "Amazing!", "author": "Bob"}],
        similar=[{"id": "s1", "name": "Similar"}],
        changelog=[{"version": "2.0.0", "title": "Major update"}])
    assert r["app"]["name"] == "SuperApp"
    assert r["stats"]["installs"] == 25000
    assert r["cta"] == "Install"
    assert len(r["sections"]) == 5
    assert len(r["top_reviews"]) == 1
