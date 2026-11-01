from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_response_cache_v9 import fleet_response_cache_v9
def test_rc2_v9():
    r = fleet_response_cache_v9([{"hits": 9000, "misses": 1000, "bytes_saved_gb": 50}])
    assert r["hit_rate"] == 90.0
    assert r["healthy"]
