from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_privilege_mgr_v9 import fleet_privilege_mgr_v9
def test_pm_v9():
    r = fleet_privilege_mgr_v9([{"status": "approved", "expired": False, "duration_min": 30}])
    assert r["approved"] == 1
    assert r["healthy"]
