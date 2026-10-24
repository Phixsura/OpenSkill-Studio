from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_container_security_v9 import fleet_container_security_v9
def test_cs3_v9():
    r = fleet_container_security_v9([{"read_only_fs": True, "non_root": True, "capabilities_dropped": True}])
    assert r["non_root"] == 1
    assert r["healthy"]
