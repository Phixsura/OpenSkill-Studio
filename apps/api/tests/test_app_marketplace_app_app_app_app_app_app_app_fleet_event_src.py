from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_event_src import fleet_event_sourcing
def test_es():
    r = fleet_event_sourcing([{"event_count": 1000000, "snapshots": 100, "replay_ms": 500}])
    assert r["total_events"] == 1000000
    assert r["fast"]
