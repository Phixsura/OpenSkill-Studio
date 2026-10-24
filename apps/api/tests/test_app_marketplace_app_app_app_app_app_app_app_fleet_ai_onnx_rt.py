from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_onnx_rt import fleet_ai_onnx_runtime
def test_onnx():
    r = fleet_ai_onnx_runtime([{"active": True, "models": 100, "inferences_24h": 100000000, "speedup_x": 3.2}])
    assert r["models"] == 100
    assert r["fast"]
