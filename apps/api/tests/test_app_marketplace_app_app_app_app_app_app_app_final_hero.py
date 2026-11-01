from app.services.app_marketplace_app_app_app_app_app_app_app_final_hero import build_hero_page

def test_hero():
    r = build_hero_page()
    assert "Build" in r["headline"]
    assert len(r["stats"]) == 4
    assert len(r["features"]) == 6
    assert r["cta"]["primary"] == "Start Building"
    assert r["trust"]["rating"] == "4.8 ⭐"
