from app.services.app_marketplace_app_detail_hero import build_app_detail_hero

def test_hero():
    h = build_app_detail_hero(
        app={"name": "SuperApp", "slug": "super-app", "description": "A great tool", "category": "connector",
             "current_version": "2.0", "price_label": "Free"},
        developer={"display_name": "DevCo", "slug": "devco", "verified": True},
        stats={"install_count": 2000, "avg_rating": 4.5, "review_count": 100},
        badges=[{"label": "Popular"}], installed=False)
    assert h["app"]["name"] == "SuperApp"
    assert h["cta"]["label"] == "Install"
    assert h["developer"]["verified"]

def test_installed():
    h = build_app_detail_hero(app={"name": "App"}, developer={}, stats={}, badges=[], installed=True)
    assert h["cta"]["label"] == "Installed"
    assert h["cta"]["disabled"]
