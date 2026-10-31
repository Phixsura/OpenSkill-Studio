from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_backup import fleet_backup_status
def test_backup():
    r = fleet_backup_status([{"age_hours": 12, "status": "ok"}, {"age_hours": 48, "status": "ok"}])
    assert r["fresh"] == 1
    assert r["stale"] == 1
    assert not r["healthy"]
