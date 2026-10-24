from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_playground import fleet_ai_playground
def test_pg():
    r = fleet_ai_playground([{"active": True, "users_24h": 50000, "experiments_24h": 200000, "models": 30}])
    assert r["users_24h"] == 50000
    assert r["popular"]
