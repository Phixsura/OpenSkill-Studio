from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_inf_prof import fleet_ai_inference_profiler
def test_ip():
    r = fleet_ai_inference_profiler([{"active": True, "profiles_24h": 1000000, "tokenize_ms": 2, "inference_ms": 50}])
    assert r["profiles_24h"] == 1000000
    assert r["optimized"]
