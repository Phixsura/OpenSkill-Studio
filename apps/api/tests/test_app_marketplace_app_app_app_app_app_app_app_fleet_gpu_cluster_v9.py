from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gpu_cluster_v9 import fleet_gpu_cluster_v9
def test_gpu_v9():
    r = fleet_gpu_cluster_v9([{"gpus": 8, "allocated": 6}, {"gpus": 8, "allocated": 4}])
    assert r["total_gpus"] == 16
    assert r["utilization_pct"] == 62.5
    assert r["healthy"]
