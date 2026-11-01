from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_deployment_rollout_v9 import fleet_deployment_rollout_v9
def test_dr3_v9():
    r = fleet_deployment_rollout_v9([{"pct": 100, "paused": False}])
    assert r["complete"] == 1
    assert r["healthy"]
