from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_optv2 import fleet_ai_model_optimizer_v2
def test_mov2():
    r = fleet_ai_model_optimizer_v2([{"active": True, "models": 100, "speedup_x": 3, "mem_reduction_pct": 40}])
    assert r["speedup_x"] == 3.0
    assert r["optimized"]
