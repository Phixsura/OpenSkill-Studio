from app.services.app_marketplace_app_geo_analytics import compute_geo_distribution, compute_country_growth

def test_distribution():
    installs = [{"country": "US", "region": "NA"}, {"country": "US", "region": "NA"},
                {"country": "DE", "region": "EU"}, {"country": "JP", "region": "APAC"}]
    r = compute_geo_distribution(installs=installs)
    assert r["top_country"] == "US"
    assert r["unique_countries"] == 3

def test_empty():
    r = compute_geo_distribution(installs=[])
    assert r["top_country"] is None

def test_growth():
    g = compute_country_growth(current={"US": 100, "DE": 50}, previous={"US": 80, "DE": 50, "JP": 10})
    assert g[0]["country"] == "US"
    assert g[0]["change"] == 20
