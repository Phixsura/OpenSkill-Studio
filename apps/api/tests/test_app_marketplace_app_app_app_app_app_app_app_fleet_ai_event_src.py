from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_event_src import fleet_ai_event_sourcing
def test_es():
    r = fleet_ai_event_sourcing([{"active": True, "events_24h": 100000000, "streams": 10000, "projections": 50}])
    assert r["events_24h"] == 100000000
    assert r["sourced"]
