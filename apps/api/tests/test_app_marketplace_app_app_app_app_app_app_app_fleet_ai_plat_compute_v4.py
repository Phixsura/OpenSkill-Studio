from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_compute_v4 import fleet_ai_compute_v4
def test_cv4():
    r = fleet_ai_compute_v4([{"active": True, "nodes": 5000, "gpus": 20000, "tflops": 10000000}])
    assert r["powerful"]
