from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_tensor import fleet_ai_tensor_compute
def test_tc():
    r = fleet_ai_tensor_compute([{"active": True, "tflops": 1000000, "jobs_24h": 50000, "util_pct": 88}])
    assert r["tflops"] == 1000000
    assert r["efficient"]
