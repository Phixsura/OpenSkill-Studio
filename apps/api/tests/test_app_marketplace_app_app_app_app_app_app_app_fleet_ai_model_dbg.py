from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_dbg import fleet_ai_model_debugger
def test_md():
    r = fleet_ai_model_debugger([{"active": True, "sessions_24h": 1000, "issues": 50, "fixed": 50}])
    assert r["issues"] == 50
    assert r["resolving"]
