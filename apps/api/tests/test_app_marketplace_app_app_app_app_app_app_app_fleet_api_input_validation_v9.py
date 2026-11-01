from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_input_validation_v9 import fleet_api_input_validation_v9
def test_aiv2_v9():
    r = fleet_api_input_validation_v9([{"validation_enabled": True, "rejected_today": 100, "schema": "v1"}])
    assert r["validated"] == 1
    assert r["healthy"]
