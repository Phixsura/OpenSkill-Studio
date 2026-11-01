from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_session_mgr_v9 import fleet_api_session_mgr_v9
def test_asm2_v9():
    r = fleet_api_session_mgr_v9([{"active": True, "expired": False, "duration_min": 30}])
    assert r["active"] == 1
    assert r["healthy"]
