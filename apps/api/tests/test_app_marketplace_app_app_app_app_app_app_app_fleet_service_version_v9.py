from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_service_version_v9 import fleet_service_version_v9
def test_sv2_v9():
    r = fleet_service_version_v9([{"on_latest": True, "version": "v1.5.0"}])
    assert r["on_latest"] == 1
    assert r["healthy"]
