from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_container_probe_v9 import fleet_container_probe_v9
def test_cp2_v9():
    r = fleet_container_probe_v9([{"liveness_probe": True, "readiness_probe": True, "startup_probe": True}])
    assert r["liveness"] == 1
    assert r["healthy"]
