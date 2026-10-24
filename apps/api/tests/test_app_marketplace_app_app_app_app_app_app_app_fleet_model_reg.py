from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_model_reg import fleet_model_registry
def test_mr():
    r = fleet_model_registry([{"models": 100, "versions": 500, "deployed_versions": 200}])
    assert r["deployment_rate"] == 40.0
