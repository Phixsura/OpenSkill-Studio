from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_error_handler_v9 import fleet_api_error_handler_v9
def test_aeh_v9():
    r = fleet_api_error_handler_v9([{"standardized": True, "retry_enabled": True, "errors_handled_today": 500}])
    assert r["standardized"] == 1
    assert r["healthy"]
