from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cilium import fleet_cilium_status
def test_cilium():
    r = fleet_cilium_status([{"ready": True, "policy_enforcement": True}, {"ready": True, "policy_enforcement": True}, {"ready": False}])
    assert r["ready"] == 2
    assert r["policy_enforced"] == 2
    assert not r["healthy"]
