from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_service_registry_v9 import fleet_service_registry_v9
def test_sreg_v9():
    r = fleet_service_registry_v9([{"registered": True, "healthy": True, "instances": 3}])
    assert r["total_instances"] == 3
    assert r["all_healthy"]
