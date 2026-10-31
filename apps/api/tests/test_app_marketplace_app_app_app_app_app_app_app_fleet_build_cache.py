from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_build_cache import fleet_build_cache
def test_cache():
    r = fleet_build_cache([{"cache_hits": 80, "cache_misses": 20, "time_saved_sec": 600}])
    assert r["hit_rate_pct"] == 80.0
    assert r["effective"]
