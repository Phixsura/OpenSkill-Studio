from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_deployment_velocity_v9 import fleet_deployment_velocity_v9
def test_dv2_v9():
    r = fleet_deployment_velocity_v9([{"deploys_per_week": 50, "avg_deploy_min": 3, "rollback_rate": 1}])
    assert r["deploys_per_week"] == 50
    assert r["healthy"]
