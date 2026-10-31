from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_event_bus import fleet_ai_event_bus
def test_eb():
    r = fleet_ai_event_bus([{"active": True, "events_24h": 100000000, "subscribers": 500, "topics": 100}])
    assert r["events_24h"] == 100000000
    assert r["connected"]
