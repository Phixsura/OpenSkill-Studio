from app.services.app_marketplace_complete_app_detail_final import build_app_detail_final

def test_full():
    p = build_app_detail_final(
        app={"name": "SuperApp", "slug": "super-app", "description": "A great tool", "category": "connector"},
        developer={"display_name": "DevCo", "verified": True},
        current_version={"version": "2.0"}, reviews={"count": 100, "avg_rating": 4.5},
        install_stats={"total": 2000}, screenshots=[{"url": "s1.png"}],
        changelog=[{"version": "2.0"}, {"version": "1.0"}], related=[{"id": "r1"}],
        pricing={"plan": "free"}, badges=[{"label": "Popular"}],
        installed=False, wishlisted=True)
    assert p["page_type"] == "app_detail_final"
    assert p["hero"]["cta"]["label"] == "Install"
    assert p["hero"]["wishlist"]["active"]
    assert len(p["tabs"]) == 6  # includes pricing
    assert "SuperApp" in p["seo"]["title"]

def test_installed_no_pricing():
    p = build_app_detail_final(
        app={"name": "App"}, developer={}, current_version=None, reviews={"count": 0},
        install_stats={}, screenshots=[], changelog=[], related=[],
        pricing=None, badges=[], installed=True, wishlisted=False)
    assert p["hero"]["cta"]["disabled"]
    assert len(p["tabs"]) == 5  # no pricing tab
