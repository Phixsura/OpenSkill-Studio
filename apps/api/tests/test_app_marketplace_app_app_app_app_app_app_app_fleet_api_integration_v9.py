from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_integration_v9 import fleet_api_integration_v9
def test_aint_v9():
    r = fleet_api_integration_v9([{"active": True, "healthy": True, "calls_today": 50000}])
    assert r["all_healthy"]
