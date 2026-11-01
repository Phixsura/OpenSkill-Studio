from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_log_pipeline_v9 import fleet_log_pipeline_v9
def test_log_v9():
    r = fleet_log_pipeline_v9([{"events_per_sec": 10000, "dropped": 0}, {"events_per_sec": 8000, "dropped": 0}])
    assert r["ingestion_rate"] == 18000
    assert r["healthy"]
