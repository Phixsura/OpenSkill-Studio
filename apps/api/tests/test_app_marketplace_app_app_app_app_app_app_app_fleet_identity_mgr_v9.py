from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_identity_mgr_v9 import fleet_identity_mgr_v9
def test_im_v9():
    r = fleet_identity_mgr_v9([{"active": True, "federated": True, "mfa": True}])
    assert r["mfa_enabled"] == 1
    assert r["healthy"]
