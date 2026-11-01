from app.services.app_marketplace_app_app_app_app_app_app_app_mkt_stats import compute_marketplace_stats

def test_stats():
    r = compute_marketplace_stats(
        total_apps=500, total_developers=200, total_installs=2500000,
        total_api_calls=50000000, avg_rating=4.3, total_reviews=15000,
        categories=8, new_apps_30d=35)
    assert r["apps_display"] == "500"
    assert r["installs_display"] == "2,500,000"
    assert r["health"] == "thriving"
    assert "+35" in r["growth_display"]
    assert r["rating_display"] == "4.3 ⭐"
