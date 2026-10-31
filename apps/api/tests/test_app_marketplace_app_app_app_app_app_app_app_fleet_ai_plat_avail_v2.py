from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_avail_v2 import fleet_ai_platform_availability_v2
def test_pav2():
    r = fleet_ai_platform_availability_v2([{"active": True, "uptime_pct": 99.999, "downtime_min": 0.5}])
    assert r["nines"] == 5
    assert r["five_nines"]
