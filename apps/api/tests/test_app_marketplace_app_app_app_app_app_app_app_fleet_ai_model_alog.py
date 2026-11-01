from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_alog import fleet_ai_model_access_log
def test_mal():
    r = fleet_ai_model_access_log([{"active": True, "accesses_24h": 1000000, "users": 5000, "models": 200}])
    assert r["accesses_24h"] == 1000000
    assert r["auditable"]
