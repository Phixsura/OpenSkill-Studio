from app.services.app_marketplace_app_app_app_app_analytics_page import build_analytics_page

def test_analytics():
    installs = [{"date": "2026-01-01", "count": 10}, {"date": "2026-01-02", "count": 25}]
    api_calls = [{"date": "2026-01-01", "count": 500}, {"date": "2026-01-02", "count": 800}]
    countries = [{"country": "US", "count": 20}, {"country": "DE", "count": 10}]
    r = build_analytics_page(app_name="SuperApp", installs=installs,
                              api_calls=api_calls, top_countries=countries)
    assert r["app_name"] == "SuperApp"
    assert r["kpis"][0]["value"] == 35
    assert r["kpis"][1]["value"] == 1300
    assert r["kpis"][2]["value"] == 15  # trend
    assert len(r["top_countries"]) == 2
