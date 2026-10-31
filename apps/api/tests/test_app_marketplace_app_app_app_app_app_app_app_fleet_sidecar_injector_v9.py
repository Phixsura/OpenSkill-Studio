from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sidecar_injector_v9 import fleet_sidecar_injector_v9
def test_si_v9():
    r = fleet_sidecar_injector_v9([{"injected": True, "pods_injected": 50, "total_pods": 50}])
    assert r["pods_with_sidecar"] == 50
    assert r["healthy"]
