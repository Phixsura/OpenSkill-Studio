from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_image_scan_v9 import fleet_image_scan_v9
def test_is2_v9():
    r = fleet_image_scan_v9([{"scanned": True, "vulnerabilities": 0}])
    assert r["clean"] == 1
    assert r["healthy"]
