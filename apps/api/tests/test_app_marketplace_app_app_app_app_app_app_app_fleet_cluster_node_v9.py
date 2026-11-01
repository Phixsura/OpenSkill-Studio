from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cluster_node_v9 import fleet_cluster_node_v9
def test_cn3_v9():
    r = fleet_cluster_node_v9([{"status": "Ready", "cpu_cores": 16, "mem_gb": 64}])
    assert r["ready"] == 1
    assert r["healthy"]
