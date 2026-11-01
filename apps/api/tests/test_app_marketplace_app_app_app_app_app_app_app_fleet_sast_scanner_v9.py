from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sast_scanner_v9 import fleet_sast_scanner_v9
def test_sast_v9():
    r = fleet_sast_scanner_v9([{"findings": 10, "critical": 0, "fixed": 8}])
    assert r["critical"] == 0
    assert r["healthy"]
