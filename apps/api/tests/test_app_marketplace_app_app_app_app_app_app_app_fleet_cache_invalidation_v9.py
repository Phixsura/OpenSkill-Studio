from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cache_invalidation_v9 import fleet_cache_invalidation_v9
def test_ci2_v9():
    r = fleet_cache_invalidation_v9([{"invalidations_today": 500, "cascade_invalidations": 50, "stale_reads": 0}])
    assert r["invalidations_today"] == 500
    assert r["healthy"]
