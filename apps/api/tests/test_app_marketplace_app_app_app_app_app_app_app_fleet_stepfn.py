from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_stepfn import fleet_stepfn_status
def test_sf():
    r = fleet_stepfn_status([{"status": "ACTIVE", "running_executions": 10, "succeeded_24h": 1000, "failed_24h": 0}])
    assert r["succeeded_24h"] == 1000
    assert r["healthy"]
