from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sagemaker import fleet_sagemaker_status
def test_sm():
    r = fleet_sagemaker_status([{"status": "InService", "instances": 4, "invocations_24h": 500000}])
    assert r["invocations_24h"] == 500000
    assert r["all_serving"]
