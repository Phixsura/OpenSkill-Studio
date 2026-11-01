from app.services.app_marketplace_app_marketplace_summary_stats import compute_marketplace_summary

def test_summary():
    s = compute_marketplace_summary(apps=500, developers=100, installs=25000, reviews=3000, api_calls=1000000, uptime_pct=99.99)
    assert len(s["headline_stats"]) == 5
    assert s["health"]["status"] == "healthy"
    assert s["growth"]["apps_per_month"] > 0
