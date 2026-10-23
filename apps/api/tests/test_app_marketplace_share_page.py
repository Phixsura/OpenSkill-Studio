from app.services.app_marketplace_share_page import build_share_page

def test_page():
    p = build_share_page(app={"name": "SuperApp", "slug": "super-app", "description": "A great tool",
                                "category": "connector", "avg_rating": 4.5, "install_count": 2000})
    assert p["page_type"] == "share"
    assert "super-app" in p["url"]
    assert "twitter.com" in p["social"]["twitter"]
    assert "linkedin.com" in p["social"]["linkedin"]
    assert "badge" in p["embed"]["badge"]
    assert p["og"]["title"] == "SuperApp"

def test_escaping():
    p = build_share_page(app={"name": 'App "with" <special>', "slug": "app-special"})
    assert "<special>" not in p["embed"]["badge"]
    assert "&lt;" in p["embed"]["badge"] or "special" in p["embed"]["badge"]
