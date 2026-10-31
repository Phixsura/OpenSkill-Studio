from app.services.app_marketplace_app_platform_landing_page import build_landing_page

def test_landing():
    stats = {"apps": 500, "developers": 200, "api_calls_daily": 5000000}
    testimonials = [{"quote": "Amazing platform!", "author": "Alice", "role": "CTO"}]
    features = [{"title": "Easy SDK", "description": "Get started in minutes", "icon": "🚀"}]
    r = build_landing_page(stats=stats, testimonials=testimonials, features=features)
    assert r["hero"]["headline"] == "Build, Ship, and Scale Apps"
    assert "500+" in r["hero"]["stats_bar"][0]["value"]
    assert len(r["features"]) == 1
    assert len(r["testimonials"]) == 1
    assert len(r["footer_links"]) == 3
