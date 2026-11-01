from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_deployment_strategy_v9 import fleet_deployment_strategy_v9
def test_ds2_v9():
    r = fleet_deployment_strategy_v9([{"strategy": "rolling"}, {"strategy": "canary"}])
    assert r["rolling"] == 1
    assert r["canary"] == 1
    assert r["healthy"]
