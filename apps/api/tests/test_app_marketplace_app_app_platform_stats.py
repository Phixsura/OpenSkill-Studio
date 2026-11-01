from app.services.app_marketplace_app_app_platform_stats import build_platform_stats

def test_stats():
    r = build_platform_stats(apps=1500, developers=350, downloads=2_500_000, reviews=8500, api_calls=150_000_000)
    assert len(r["stats"]) == 5
    assert r["stats"][0]["display"] == "1.5K"
    assert r["stats"][2]["display"] == "2.5M"
    assert r["stats"][4]["display"] == "150.0M"
