from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_maintenance_window_v9 import fleet_maintenance_window_v9
def test_mw_v9():
    r = fleet_maintenance_window_v9([{"status": "completed"}, {"status": "upcoming"}])
    assert r["completed"] == 1
    assert r["in_progress"] == 0
    assert r["healthy"]
