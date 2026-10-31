from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_observability_v9 import fleet_api_observability_v9
def test_aobs_v9():
    r = fleet_api_observability_v9([{"instrumented": True, "tracing": True, "metrics": True, "structured_logs": True}])
    assert r["instrumented"] == 1
    assert r["healthy"]
