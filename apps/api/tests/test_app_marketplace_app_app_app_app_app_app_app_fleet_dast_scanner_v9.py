from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dast_scanner_v9 import fleet_dast_scanner_v9
def test_dast_v9():
    r = fleet_dast_scanner_v9([{"completed": True, "vulnerabilities": 0, "duration_min": 30}])
    assert r["completed"] == 1
    assert r["healthy"]
