from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_build_cache_v9 import fleet_build_cache_v9
def test_bc2_v9():
    r = fleet_build_cache_v9([{"hits": 900, "misses": 100, "size_gb": 50, "time_saved_min": 500}])
    assert r["hit_rate"] == 90.0
    assert r["healthy"]
