from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_sandbox import fleet_ai_sandbox
def test_sb():
    r = fleet_ai_sandbox([{"running": True, "executions_24h": 500000, "isolated": True}])
    assert r["executions_24h"] == 500000
    assert r["secure"]
