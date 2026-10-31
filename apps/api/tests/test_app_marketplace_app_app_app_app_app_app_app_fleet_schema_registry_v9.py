from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_schema_registry_v9 import fleet_schema_registry_v9
def test_schema_v9():
    r = fleet_schema_registry_v9([{"compatible": True, "versions": 5}, {"compatible": True, "versions": 3}])
    assert r["total_versions"] == 8
    assert r["breaking_changes"] == 0
    assert r["healthy"]
