from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_crd_manager_v9 import fleet_crd_manager_v9
def test_crd_v9():
    r = fleet_crd_manager_v9([{"status": "established", "instances": 100, "versions": 3}])
    assert r["established"] == 1
    assert r["healthy"]
