from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_dbg_v2 import fleet_ai_model_debugger_v2
def test_mdv2():
    r = fleet_ai_model_debugger_v2([{"active": True, "sessions_24h": 5000, "breakpoints": 200, "resolved": 180}])
    assert r["resolved"] == 180
    assert r["debugging"]
