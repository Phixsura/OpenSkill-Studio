from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_key_mgr_v9 import fleet_api_key_mgr_v9
def test_akm_v9():
    r = fleet_api_key_mgr_v9([{"active": True, "revoked": False, "expired": False}])
    assert r["active"] == 1
    assert r["healthy"]
