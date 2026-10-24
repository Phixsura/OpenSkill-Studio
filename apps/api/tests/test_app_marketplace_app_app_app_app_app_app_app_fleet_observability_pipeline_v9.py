from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_observability_pipeline_v9 import fleet_observability_pipeline_v9
def test_op2_v9():
    r = fleet_observability_pipeline_v9([{"active": True, "events_per_sec": 100000, "dropped": 0}])
    assert r["throughput_eps"] == 100000
    assert r["healthy"]
