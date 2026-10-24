from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_deployment_history_v9 import fleet_deployment_history_v9
def test_dh_v9():
    r = fleet_deployment_history_v9([{"result": "success", "env": "prod"}, {"result": "success", "env": "staging"}])
    assert r["success"] == 2
    assert r["environments"] == 2
    assert r["healthy"]
