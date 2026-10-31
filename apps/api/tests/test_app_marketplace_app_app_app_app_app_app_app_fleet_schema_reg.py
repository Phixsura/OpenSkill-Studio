from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_schema_reg import fleet_schema_registry
def test_schema():
    r = fleet_schema_registry([{"compatible": True}, {"compatible": False}])
    assert r["breaking"] == 1
    assert not r["safe"]
