from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_websocket_v9 import fleet_api_websocket_v9
def test_aws2_v9():
    r = fleet_api_websocket_v9([{"connections": 10000, "messages_per_sec": 50000, "errors_today": 0}])
    assert r["active_connections"] == 10000
    assert r["healthy"]
