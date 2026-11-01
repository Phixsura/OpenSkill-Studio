from app.services.app_marketplace_app_app_geo_analytics import analyze_geo_distribution

def test_geo():
    installs = [{"country": "US"}] * 50 + [{"country": "GB"}] * 30 + [{"country": "DE"}] * 20
    r = analyze_geo_distribution(installs=installs)
    assert r["total_installs"] == 100
    assert r["top_country"] == "US"
    assert r["countries"][0]["pct"] == 50.0
    assert r["unique_countries"] == 3

def test_empty():
    r = analyze_geo_distribution(installs=[])
    assert r["total_installs"] == 0
    assert r["top_country"] is None
