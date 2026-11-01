from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_data_valid import fleet_ai_data_validator
def test_dv():
    r = fleet_ai_data_validator([{"active": True, "validated_24h": 50000000, "issues": 50000, "rules": 50}])
    assert r["validated_24h"] == 50000000
    assert r["thorough"]
