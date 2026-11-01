from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_serve_v3 import fleet_ai_model_serving_v3
def test_sv3():
    r = fleet_ai_model_serving_v3([{"active": True, "models": 200, "rps": 500000, "p99_ms": 30, "gpu_util": 85}])
    assert r["rps"] == 500000
    assert r["performant"]
