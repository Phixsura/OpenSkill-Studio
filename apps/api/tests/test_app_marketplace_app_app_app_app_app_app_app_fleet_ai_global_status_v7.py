from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_global_status_v7 import fleet_ai_global_status_v7
def test_gsv7():
    r = fleet_ai_global_status_v7([{"active": True, "services": 1000, "healthy": 1000, "requests_24h": 50000000000, "uptime_pct": 99.9999}])
    assert "OPERATIONAL" in r["global_status"]
    assert r["uptime"] == 99.9999
