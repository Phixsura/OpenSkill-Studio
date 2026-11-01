from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_gpu_pool_v2 import fleet_ai_gpu_pool_v2
def test_gpv2():
    r = fleet_ai_gpu_pool_v2([{"active": True, "gpus": 10000, "allocated": 8500, "queue": 50}])
    assert r["utilization"] == 85.0
    assert r["efficient"]
