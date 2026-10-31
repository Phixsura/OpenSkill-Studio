from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_uptime_mon import fleet_ai_uptime_monitor
def test_um():
    r = fleet_ai_uptime_monitor([{"active": True, "endpoints": 200, "uptime_pct": 99.99, "checks_24h": 1000000}])
    assert r["uptime_pct"] == 99.99
    assert r["reliable"]
