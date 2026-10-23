from app.services.app_marketplace_app_app_app_app_app_app_app_geo_distribution import analyze_distribution, find_nearest_region

def test_distribution():
    reqs = [{"region": "us-east"}] * 50 + [{"region": "eu-west"}] * 30 + [{"region": "ap-east"}] * 20
    r = analyze_distribution(reqs)
    assert r["total"] == 100
    assert r["top_region"] == "us-east"
    assert r["unique_regions"] == 3
    assert r["regions"][0]["pct"] == 50.0

def test_nearest():
    r = find_nearest_region(48.9, 2.3)  # Paris
    assert r["nearest"] == "eu-west"
