from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_temporal import fleet_temporal_status
def test_tmp():
    r = fleet_temporal_status([{"healthy": True, "running_workflows": 500, "completed_24h": 10000}])
    assert r["running_workflows"] == 500
    assert r["all_healthy"]
