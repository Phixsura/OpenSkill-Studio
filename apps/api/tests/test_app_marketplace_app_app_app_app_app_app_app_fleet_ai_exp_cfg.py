from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_exp_cfg import fleet_ai_experiment_config
def test_ec():
    r = fleet_ai_experiment_config([{"active": True, "configs": 1000, "templates": 50, "overrides_24h": 200}])
    assert r["configs"] == 1000
    assert r["organized"]
