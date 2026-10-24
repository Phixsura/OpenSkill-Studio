from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_uptime_monitor_v9 import fleet_uptime_monitor_v9
def test_um_v9():
    r = fleet_uptime_monitor_v9([{"status": "up", "response_ms": 50}, {"status": "up", "response_ms": 30}])
    assert r["uptime_pct"] == 100.0
    assert r["healthy"]
