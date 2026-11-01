from app.services.app_marketplace_app_app_app_app_app_app_app_landing_data import build_landing_page_data

def test_landing():
    r = build_landing_page_data()
    assert "Developer Platform" in r["hero"]["headline"]
    assert len(r["features"]) == 6
    assert len(r["testimonials"]) == 2
    assert r["stats"]["uptime"] == "99.99%"
