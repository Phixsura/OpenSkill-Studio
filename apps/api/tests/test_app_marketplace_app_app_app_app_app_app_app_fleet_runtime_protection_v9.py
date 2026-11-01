from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_runtime_protection_v9 import fleet_runtime_protection_v9
def test_rp2_v9():
    r = fleet_runtime_protection_v9([{"active": True, "threats_blocked": 50, "processes": 500}])
    assert r["threats_blocked"] == 50
    assert r["healthy"]
