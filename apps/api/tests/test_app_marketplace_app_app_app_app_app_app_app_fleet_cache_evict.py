from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cache_evict import fleet_cache_eviction
def test_evict():
    r = fleet_cache_eviction([{"evictions_per_sec": 50}, {"evictions_per_sec": 200}])
    assert r["total_evictions_per_sec"] == 250
    assert r["high_eviction"] == 1
    assert r["needs_resize"]
