from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_compile import fleet_ai_model_compiler
def test_mc():
    r = fleet_ai_model_compiler([{"active": True, "models": 200, "speedup_x": 3, "targets": ["gpu", "cpu", "tpu", "edge"]}])
    assert r["targets"] == 4
    assert r["optimized"]
