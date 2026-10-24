from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_websocket import fleet_websocket_metrics
def test_ws():
    r = fleet_websocket_metrics([{"connections": 800, "max_connections": 1000, "errors_per_min": 0}])
    assert r["util_pct"] == 80.0
    assert r["healthy"]
