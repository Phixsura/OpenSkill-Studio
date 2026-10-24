from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_change_log_v9 import fleet_api_change_log_v9
def test_acl2_v9():
    r = fleet_api_change_log_v9([{"breaking": False, "consumers_notified": 100}])
    assert r["breaking"] == 0
    assert r["healthy"]
