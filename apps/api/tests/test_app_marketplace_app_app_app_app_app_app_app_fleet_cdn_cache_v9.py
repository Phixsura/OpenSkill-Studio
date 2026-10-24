from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cdn_cache_v9 import fleet_cdn_cache_v9
def test_cdn_v9():
    r = fleet_cdn_cache_v9([{"hit_ratio": 0.95, "bandwidth_gbps": 100, "errors": 0}])
    assert r["avg_hit_ratio"] == 0.95
    assert r["healthy"]
