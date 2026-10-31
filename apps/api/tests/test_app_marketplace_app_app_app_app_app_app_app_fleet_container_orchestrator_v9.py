from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_container_orchestrator_v9 import fleet_container_orchestrator_v9
def test_co2_v9():
    r = fleet_container_orchestrator_v9([{"control_plane_healthy": True, "etcd_healthy": True, "api_server_latency_ms": 10}])
    assert r["control_plane_ok"] == 1
    assert r["healthy"]
