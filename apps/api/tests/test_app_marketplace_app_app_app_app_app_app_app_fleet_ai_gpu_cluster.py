from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_gpu_cluster import fleet_ai_gpu_cluster
def test_gc():
    r = fleet_ai_gpu_cluster([{"active": True, "gpus": 1000, "utilized": 850, "tflops": 500000}])
    assert r["utilization"] == 85.0
    assert r["efficient"]
