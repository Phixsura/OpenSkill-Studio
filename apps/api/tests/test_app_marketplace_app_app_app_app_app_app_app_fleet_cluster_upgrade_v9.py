from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cluster_upgrade_v9 import fleet_cluster_upgrade_v9
def test_cu2_v9():
    r = fleet_cluster_upgrade_v9([{"upgraded": True, "upgrading": False, "pending": False}])
    assert r["upgraded"] == 1
    assert r["healthy"]
