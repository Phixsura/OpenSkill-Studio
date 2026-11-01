from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_wasm_runtime_v9 import fleet_wasm_runtime_v9
def test_wasm_v9():
    r = fleet_wasm_runtime_v9([{"loaded": True, "invocations_today": 100000, "avg_exec_ms": 0.5}])
    assert r["invocations_today"] == 100000
    assert r["healthy"]
