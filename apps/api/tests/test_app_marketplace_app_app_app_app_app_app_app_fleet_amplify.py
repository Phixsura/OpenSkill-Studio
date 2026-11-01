from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_amplify import fleet_amplify_status
def test_amp():
    r = fleet_amplify_status([{"deployed": True, "backends": 3, "branches": 5}])
    assert r["backends"] == 3
    assert r["all_deployed"]
