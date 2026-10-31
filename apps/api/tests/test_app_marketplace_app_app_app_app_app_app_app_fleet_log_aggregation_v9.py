from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_log_aggregation_v9 import fleet_log_aggregation_v9
def test_la2_v9():
    r = fleet_log_aggregation_v9([{"active": True, "events_per_sec": 50000, "storage_gb": 500}])
    assert r["events_per_sec"] == 50000
    assert r["healthy"]
