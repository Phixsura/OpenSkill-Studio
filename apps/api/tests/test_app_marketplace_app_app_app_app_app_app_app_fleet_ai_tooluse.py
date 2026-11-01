from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_tooluse import fleet_ai_tooluse
def test_tu():
    r = fleet_ai_tooluse([{"active": True, "tool_calls_24h": 5000000, "tools": 100, "success_rate": 97}])
    assert r["tool_calls_24h"] == 5000000
    assert r["success_rate"] == 97.0
