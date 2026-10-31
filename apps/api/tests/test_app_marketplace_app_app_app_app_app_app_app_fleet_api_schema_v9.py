from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_schema_v9 import fleet_api_schema_v9
def test_asch_v9():
    r = fleet_api_schema_v9([{"valid": True, "versions": 5, "breaking_change": False}])
    assert r["breaking_changes"] == 0
    assert r["healthy"]
