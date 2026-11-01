from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dragonfly import fleet_dragonfly_status
def test_df():
    r = fleet_dragonfly_status([{"running": True, "memory_gb": 64, "ops_per_sec": 2000000}])
    assert r["memory_gb"] == 64
    assert r["high_perf"]
