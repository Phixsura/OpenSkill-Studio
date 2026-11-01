from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_deploy_pipe import fleet_deploy_pipeline
def test_pipe():
    r = fleet_deploy_pipeline([{"status": "passing", "duration_min": 10}, {"status": "failing", "duration_min": 15}])
    assert r["passing"] == 1
    assert r["avg_duration_min"] == 12.5
    assert not r["healthy"]
