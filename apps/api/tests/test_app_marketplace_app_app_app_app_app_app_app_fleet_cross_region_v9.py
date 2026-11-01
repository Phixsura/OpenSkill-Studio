from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cross_region_v9 import fleet_cross_region_v9
def test_xr_v9():
    r = fleet_cross_region_v9([{"role": "primary"}, {"role": "replica", "replication_lag_ms": 50}])
    assert r["replicas"] == 1
    assert r["total_lag_ms"] == 50
    assert r["healthy"]
