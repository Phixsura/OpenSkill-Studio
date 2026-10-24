from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_mcp import fleet_ai_mcp
def test_mcp():
    r = fleet_ai_mcp([{"running": True, "tools": 50, "resources": 100, "calls_24h": 2000000}])
    assert r["tools"] == 50
    assert r["calls_24h"] == 2000000
