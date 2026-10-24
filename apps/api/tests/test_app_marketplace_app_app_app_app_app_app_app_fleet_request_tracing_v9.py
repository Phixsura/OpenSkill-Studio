from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_request_tracing_v9 import fleet_request_tracing_v9
def test_rt2_v9():
    r = fleet_request_tracing_v9([{"sampled": True, "spans": 12, "has_error": False}])
    assert r["sampled"] == 1
    assert r["healthy"]
