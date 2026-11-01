from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_inf_opt_v2 import fleet_ai_inference_optimizer_v2
def test_iov2():
    r = fleet_ai_inference_optimizer_v2([{"active": True, "models": 100, "speedup_x": 4, "techniques": ["quantization", "pruning", "distillation", "caching"]}])
    assert r["speedup_x"] == 4.0
    assert r["accelerated"]
