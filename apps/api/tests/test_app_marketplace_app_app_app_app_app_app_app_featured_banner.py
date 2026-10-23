from app.services.app_marketplace_app_app_app_app_app_app_app_featured_banner import build_featured_banners

def test_banners():
    r = build_featured_banners([
        {"title": "New: SSO Support", "subtitle": "Enterprise-grade authentication", "cta": "Enable SSO", "icon": "🔐"},
        {"title": "Developer Contest", "subtitle": "Win prizes!", "cta": "Enter Now", "icon": "🏆"},
    ])
    assert r["count"] == 2
    assert r["banners"][0]["title"] == "New: SSO Support"
    assert r["banners"][1]["cta"] == "Enter Now"
