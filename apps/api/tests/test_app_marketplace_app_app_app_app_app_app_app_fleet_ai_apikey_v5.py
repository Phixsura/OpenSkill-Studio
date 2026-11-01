from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_apikey_v5 import fleet_ai_apikey_v5
def test_akv5():
    r = fleet_ai_apikey_v5([{"active": True, "keys": 100000, "created": 500, "revoked": 100, "scoped": True}])
    assert r["keys"] == 100000
    assert r["governed"]
