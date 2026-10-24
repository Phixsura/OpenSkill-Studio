from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_service_account_v9 import fleet_service_account_v9
def test_sa2_v9():
    r = fleet_service_account_v9([{"active": True, "over_privileged": False, "used_this_week": True}])
    assert r["over_privileged"] == 0
    assert r["healthy"]
