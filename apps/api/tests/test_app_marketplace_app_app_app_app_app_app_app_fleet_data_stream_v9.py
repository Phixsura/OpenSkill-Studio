from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_data_stream_v9 import fleet_data_stream_v9
def test_ds3_v9():
    r = fleet_data_stream_v9([{"active": True, "records_per_sec": 100000, "consumer_lag": 5}])
    assert r["records_per_sec"] == 100000
    assert r["healthy"]
