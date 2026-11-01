from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_keda import fleet_keda_status
def test_keda():
    r = fleet_keda_status([{"active": True, "triggered": True}, {"active": True, "triggered": False}, {"active": False}])
    assert r["active"] == 2
    assert r["triggered"] == 1
    assert not r["all_active"]
