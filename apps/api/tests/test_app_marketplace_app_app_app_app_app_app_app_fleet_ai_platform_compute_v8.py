from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_compute_v8 import fleet_ai_compute_v8
def test_cv8():
    r = fleet_ai_compute_v8([{"active": True, "nodes": 50000, "gpus": 200000, "tflops": 100000000, "util_pct": 88}])
    assert r["gpus"] == 200000
    assert r["efficient"]
