from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_event_bus_v9 import fleet_event_bus_v9
def test_bus_v9():
    r = fleet_event_bus_v9([{"active": True, "events_per_sec": 20000, "subscribers": 50}])
    assert r["events_per_sec"] == 20000
    assert r["healthy"]
