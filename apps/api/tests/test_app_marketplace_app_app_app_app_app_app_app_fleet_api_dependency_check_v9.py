from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_dependency_check_v9 import fleet_api_dependency_check_v9
def test_adc_v9():
    r = fleet_api_dependency_check_v9([{"healthy": True, "degraded": False, "down": False}])
    assert r["all_healthy"]
