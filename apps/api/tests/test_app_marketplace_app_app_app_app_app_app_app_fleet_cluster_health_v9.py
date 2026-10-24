from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cluster_health_v9 import fleet_cluster_health_v9
def test_ch_v9():
    r = fleet_cluster_health_v9([{"status": "healthy", "nodes": 50, "pods": 500, "cpu_pct": 45}])
    assert r["total_nodes"] == 50
    assert r["healthy"]
