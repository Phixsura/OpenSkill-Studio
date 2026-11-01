from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_phoenix import fleet_phoenix_status
def test_phx():
    r = fleet_phoenix_status([{"running": True, "channels": 50, "ws_connections": 10000}])
    assert r["ws_connections"] == 10000
    assert r["all_running"]
