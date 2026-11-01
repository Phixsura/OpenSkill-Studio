from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_status_v2 import fleet_ai_status_page_v2
def test_spv2():
    r = fleet_ai_status_page_v2([{"active": True, "components": 100, "operational": 100, "incidents": 3, "uptime_pct": 99.99}])
    assert "OPERATIONAL" in r["status"]
