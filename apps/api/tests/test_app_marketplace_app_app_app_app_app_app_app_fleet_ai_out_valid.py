from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_out_valid import fleet_ai_output_validator
def test_ov():
    r = fleet_ai_output_validator([{"active": True, "validated_24h": 5000000, "rejected_24h": 1000, "rules": 50}])
    assert r["validated_24h"] == 5000000
    assert r["enforcing"]
