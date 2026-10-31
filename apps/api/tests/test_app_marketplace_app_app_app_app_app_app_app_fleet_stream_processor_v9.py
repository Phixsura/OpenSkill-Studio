from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_stream_processor_v9 import fleet_stream_processor_v9
def test_sp_v9():
    r = fleet_stream_processor_v9([{"active": True, "events_per_sec": 50000, "consumer_lag": 10}])
    assert r["throughput"] == 50000
    assert r["healthy"]
