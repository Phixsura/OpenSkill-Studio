from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_deployment_pipeline_v9 import fleet_api_deployment_pipeline_v9
def test_adp2_v9():
    r = fleet_api_deployment_pipeline_v9([{"status": "success", "duration_sec": 120}])
    assert r["success"] == 1
    assert r["healthy"]
