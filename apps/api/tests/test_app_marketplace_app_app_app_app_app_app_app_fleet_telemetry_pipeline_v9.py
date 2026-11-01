from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_telemetry_pipeline_v9 import fleet_telemetry_pipeline_v9
def test_tp_v9():
    r = fleet_telemetry_pipeline_v9([{"active": True, "spans_per_sec": 50000, "metrics_per_sec": 100000}])
    assert r["spans_per_sec"] == 50000
    assert r["healthy"]
