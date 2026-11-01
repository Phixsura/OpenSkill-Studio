from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_opt_v3 import fleet_ai_model_optimizer_v3
def test_mov3():
    r = fleet_ai_model_optimizer_v3([{"active": True, "models": 300, "speedup_x": 8, "techniques": ["quantization", "pruning", "distillation", "flash_attention", "speculative"]}])
    assert r["speedup_x"] == 8.0
    assert r["ultimate"]
