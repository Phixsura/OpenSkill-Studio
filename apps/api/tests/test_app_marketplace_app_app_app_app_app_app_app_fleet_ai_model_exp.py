from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_exp import fleet_ai_model_export
def test_me():
    r = fleet_ai_model_export([{"active": True, "exports_24h": 5000, "formats": ["onnx", "safetensors", "gguf", "tflite"], "size_gb": 1000}])
    assert r["formats"] == 4
    assert r["versatile"]
