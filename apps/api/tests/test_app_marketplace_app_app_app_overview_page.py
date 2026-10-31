from app.services.app_marketplace_app_app_app_overview_page import build_app_overview

def test_overview():
    app = {"name": "SuperApp", "icon": "🚀", "tagline": "Do more", "author": "Alice",
           "verified": True, "version": "2.0.0", "downloads": 25000, "rating": 4.7,
           "description": "A powerful app", "pricing": "Free", "categories": ["tools"],
           "tags": ["productivity"]}
    r = build_app_overview(app=app, reviews_summary={"total": 120})
    assert r["header"]["name"] == "SuperApp"
    assert r["header"]["verified"]
    assert r["stats"]["downloads"] == 25000
    assert r["stats"]["review_count"] == 120
    assert r["install_cta"] == "Install"

def test_paid():
    app = {"name": "ProApp", "pricing": "$9/mo"}
    r = build_app_overview(app=app)
    assert "Subscribe" in r["install_cta"]
