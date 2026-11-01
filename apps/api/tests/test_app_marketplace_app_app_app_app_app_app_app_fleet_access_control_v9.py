from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_access_control_v9 import fleet_access_control_v9
def test_ac_v9():
    r = fleet_access_control_v9([{"active": True, "denials": 0, "role": "admin"}, {"active": True, "denials": 2, "role": "viewer"}])
    assert r["unique_roles"] == 2
    assert r["healthy"]
