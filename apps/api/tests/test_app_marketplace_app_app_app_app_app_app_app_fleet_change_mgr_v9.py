from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_change_mgr_v9 import fleet_change_mgr_v9
def test_cm_v9():
    r = fleet_change_mgr_v9([{"status": "approved"}, {"status": "approved"}])
    assert r["approved"] == 2
    assert r["pending"] == 0
    assert r["healthy"]
