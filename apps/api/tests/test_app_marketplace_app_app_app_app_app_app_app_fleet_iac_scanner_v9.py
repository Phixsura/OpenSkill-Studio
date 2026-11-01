from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_iac_scanner_v9 import fleet_iac_scanner_v9
def test_iac_v9():
    r = fleet_iac_scanner_v9([{"passed": True, "misconfigurations": 0, "critical": 0}])
    assert r["critical"] == 0
    assert r["healthy"]
