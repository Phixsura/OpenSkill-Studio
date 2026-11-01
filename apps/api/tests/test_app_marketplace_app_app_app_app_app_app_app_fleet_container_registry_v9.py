from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_container_registry_v9 import fleet_container_registry_v9
def test_cr_v9():
    r = fleet_container_registry_v9([{"scanned": True, "vulnerabilities": 0, "size_mb": 512}])
    assert r["scanned"] == 1
    assert r["vulnerabilities"] == 0
    assert r["healthy"]
