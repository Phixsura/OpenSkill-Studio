from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_secret_scanner_v9 import fleet_secret_scanner_v9
def test_ss2_v9():
    r = fleet_secret_scanner_v9([{"scanned": True, "secrets_found": 2, "remediated": 2}])
    assert r["scanned"] == 1
    assert r["healthy"]
