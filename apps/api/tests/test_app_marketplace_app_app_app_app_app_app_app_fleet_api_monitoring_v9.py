from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_monitoring_v9 import fleet_api_monitoring_v9
def test_amon_v9():
    r = fleet_api_monitoring_v9([{"active": True, "alerts_firing": 0, "uptime_pct": 99.99}])
    assert r["avg_uptime_pct"] == 99.99
    assert r["healthy"]
