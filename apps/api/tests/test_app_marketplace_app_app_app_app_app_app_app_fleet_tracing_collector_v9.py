from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_tracing_collector_v9 import fleet_tracing_collector_v9
def test_trace_v9():
    r = fleet_tracing_collector_v9([{"spans_per_sec": 50000, "dropped": 0, "storage_gb": 200}])
    assert r["spans_per_sec"] == 50000
    assert r["healthy"]
