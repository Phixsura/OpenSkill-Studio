from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_vol_snap import fleet_vol_snapshots
def test_snap():
    r = fleet_vol_snapshots([{"has_snapshot": True, "snapshot_age_hours": 12}, {"has_snapshot": True, "snapshot_age_hours": 48}])
    assert r["stale_snapshots"] == 1
    assert not r["all_fresh"]
