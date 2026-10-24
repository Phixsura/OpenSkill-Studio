from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_playground import fleet_ai_playground
def test_pg():
    r = fleet_ai_playground([{"active": True, "sessions_24h": 50000, "prompts_24h": 500000}])
    assert r["sessions_24h"] == 50000
    assert r["popular"]
