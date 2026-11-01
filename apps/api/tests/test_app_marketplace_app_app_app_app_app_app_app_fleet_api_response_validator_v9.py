from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_response_validator_v9 import fleet_api_response_validator_v9
def test_arv_v9():
    r = fleet_api_response_validator_v9([{"active": True, "violations_today": 0, "validated_today": 50000}])
    assert r["violations_today"] == 0
    assert r["healthy"]
