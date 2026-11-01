from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_event_schema_v9 import fleet_event_schema_v9
def test_es2_v9():
    r = fleet_event_schema_v9([{"compatible": True, "breaking": False, "versions": 5}])
    assert r["breaking"] == 0
    assert r["healthy"]
