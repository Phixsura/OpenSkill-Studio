from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_k8s_upgrade_v9 import fleet_k8s_upgrade_v9
def test_ku_v9():
    r = fleet_k8s_upgrade_v9([{"up_to_date": True, "upgrading": False, "outdated": False}])
    assert r["current"] == 1
    assert r["healthy"]
