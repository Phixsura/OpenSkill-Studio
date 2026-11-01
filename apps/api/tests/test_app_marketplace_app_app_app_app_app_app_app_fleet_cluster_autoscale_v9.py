from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cluster_autoscale_v9 import fleet_cluster_autoscale_v9
def test_ca_v9():
    r = fleet_cluster_autoscale_v9([{"nodes": 10, "min_nodes": 3, "max_nodes": 20}])
    assert r["total_nodes"] == 10
    assert r["healthy"]
