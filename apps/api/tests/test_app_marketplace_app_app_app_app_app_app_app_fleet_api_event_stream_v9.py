from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_event_stream_v9 import fleet_api_event_stream_v9
def test_aes2_v9():
    r = fleet_api_event_stream_v9([{"active": True, "consumers": 50, "events_per_sec": 10000}])
    assert r["events_per_sec"] == 10000
    assert r["healthy"]
