from app.services.app_marketplace_app_app_app_app_app_app_landing_page import build_landing_page

def test_landing():
    r = build_landing_page()
    assert r["hero"]["title"] == "Build, Publish, and Scale Apps"
    assert len(r["features"]) == 6
    assert len(r["stats"]) == 4
    assert len(r["testimonials"]) == 2
