from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dependency_scanner_v9 import fleet_dependency_scanner_v9
def test_ds_v9():
    r = fleet_dependency_scanner_v9([{"vulnerable": False, "outdated": False, "severity": "none"}])
    assert r["vulnerable"] == 0
    assert r["critical"] == 0
    assert r["healthy"]
