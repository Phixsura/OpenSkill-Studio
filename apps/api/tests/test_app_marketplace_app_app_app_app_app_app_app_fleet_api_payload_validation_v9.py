from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_payload_validation_v9 import fleet_api_payload_validation_v9
def test_apv2_v9():
    r = fleet_api_payload_validation_v9([{"active": True, "rejected_today": 50, "validated_today": 100000}])
    assert r["validated_today"] == 100000
    assert r["healthy"]
