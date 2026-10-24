from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_contract import fleet_api_contract_validator
def test_contract():
    r = fleet_api_contract_validator([{"schema_valid": True}, {"schema_valid": False}])
    assert r["invalid"] == 1
    assert not r["all_valid"]
