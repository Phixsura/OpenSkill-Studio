from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_snapshot_mgr_v9 import fleet_snapshot_mgr_v9
def test_snap_v9():
    r = fleet_snapshot_mgr_v9([{"status": "available", "size_gb": 100, "age_days": 5}])
    assert r["available"] == 1
    assert r["stale"] == 0
    assert r["healthy"]
