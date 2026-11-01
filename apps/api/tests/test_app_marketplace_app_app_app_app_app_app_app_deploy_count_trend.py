from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_count_trend import deploy_count_trend
def test_accelerating():
    r = deploy_count_trend([{"deploys": 5}, {"deploys": 6}, {"deploys": 10}, {"deploys": 12}])
    assert r["trend"] == "accelerating"
