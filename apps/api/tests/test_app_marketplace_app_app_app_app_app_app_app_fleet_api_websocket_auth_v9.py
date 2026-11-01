from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_websocket_auth_v9 import fleet_api_websocket_auth_v9
def test_awsa_v9():
    r = fleet_api_websocket_auth_v9([{"authenticated": True, "auth_method": "token", "rejected_today": 0}])
    assert r["authenticated"] == 1
    assert r["healthy"]
