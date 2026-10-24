from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_service_registry_v9 import fleet_api_service_registry_v9
def test_asr2_v9():
    r = fleet_api_service_registry_v9([{"registered": True, "healthy": True, "version": "v1"}])
    assert r["all_healthy"]
