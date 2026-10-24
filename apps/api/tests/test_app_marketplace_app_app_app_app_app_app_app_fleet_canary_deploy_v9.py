from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_canary_deploy_v9 import fleet_canary_deploy_v9
def test_canary_v9():
    r = fleet_canary_deploy_v9([{"phase": "promoted"}, {"phase": "promoted"}, {"phase": "canary"}])
    assert r["promoted"] == 2
    assert r["healthy"]
