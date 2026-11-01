from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_schema_reg import fleet_ai_schema_registry
def test_sr():
    r = fleet_ai_schema_registry([{"active": True, "schemas": 300, "versions": 1500, "validations_24h": 50000000}])
    assert r["schemas"] == 300
    assert r["governed"]
