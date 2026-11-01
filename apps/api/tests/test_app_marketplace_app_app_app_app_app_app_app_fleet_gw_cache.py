from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gw_cache import fleet_gw_cache
def test_gw_cache():
    r = fleet_gw_cache([{"cache_enabled": True, "cache_hits": 900, "cache_misses": 100}, {"cache_enabled": False}])
    assert r["cached"] == 1
    assert r["hit_rate"] == 90.0
    assert r["effective"]
