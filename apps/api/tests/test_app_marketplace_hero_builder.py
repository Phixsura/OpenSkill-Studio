from app.services.app_marketplace_hero_builder import build_hero

def test_hero():
    h = build_hero(total_apps=100, total_developers=20)
    assert h["total_apps"] == 100
    assert "Explore" in h["cta_primary"]["label"]
