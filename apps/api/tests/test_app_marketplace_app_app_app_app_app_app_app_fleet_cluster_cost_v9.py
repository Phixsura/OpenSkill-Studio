from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cluster_cost_v9 import fleet_cluster_cost_v9
def test_cc3_v9():
    r = fleet_cluster_cost_v9([{"monthly_cost": 10000, "compute_cost": 6000, "storage_cost": 2000, "network_cost": 2000}])
    assert r["total_monthly"] == 10000
    assert r["healthy"]
