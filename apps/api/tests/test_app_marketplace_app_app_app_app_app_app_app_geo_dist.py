from app.services.app_marketplace_app_app_app_app_app_app_app_geo_dist import aggregate_geo

def test_geo():
    reqs = [{"region": "us-east"}] * 50 + [{"region": "eu-west"}] * 30 + [{"region": "ap-southeast"}] * 20
    r = aggregate_geo(reqs)
    assert r["total"] == 100
    assert r["region_count"] == 3
    assert r["top_region"] == "us-east"
    assert r["distribution"][0]["pct"] == 50.0

def test_empty():
    r = aggregate_geo([])
    assert r["total"] == 0
