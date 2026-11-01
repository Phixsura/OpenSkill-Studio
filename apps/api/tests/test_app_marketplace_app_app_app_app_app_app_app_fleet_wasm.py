from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_wasm import fleet_wasm_status
def test_wasm():
    r = fleet_wasm_status([{"loaded": True, "executions_24h": 1000000, "avg_exec_ms": 2}])
    assert r["executions_24h"] == 1000000
    assert r["performant"]
