from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_onnx import fleet_onnx_status
def test_onnx():
    r = fleet_onnx_status([{"running": True, "models": 15, "inf_per_sec": 100000}])
    assert r["models"] == 15
    assert r["all_running"]
