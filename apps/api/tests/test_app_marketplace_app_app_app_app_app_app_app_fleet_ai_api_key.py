from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_api_key import fleet_ai_api_key_manager
def test_ak():
    r = fleet_ai_api_key_manager([{"active": True, "keys_active": 10000, "revoked_24h": 50, "requests_24h": 200000000}])
    assert r["keys_active"] == 10000
    assert r["managed"]
