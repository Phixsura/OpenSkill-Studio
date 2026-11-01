from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_distributed_tracing_v9 import fleet_distributed_tracing_v9
def test_dt2_v9():
    r = fleet_distributed_tracing_v9([{"tracing_enabled": True, "spans_per_sec": 50000, "sampling_rate": 10}])
    assert r["instrumented"] == 1
    assert r["healthy"]
