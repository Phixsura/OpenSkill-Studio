from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cloudfront import fleet_cloudfront_status
def test_cf():
    r = fleet_cloudfront_status([{"status": "Deployed", "requests_24h": 100000000, "cache_hit_pct": 95}])
    assert r["cache_hit_pct"] == 95.0
    assert r["all_deployed"]
