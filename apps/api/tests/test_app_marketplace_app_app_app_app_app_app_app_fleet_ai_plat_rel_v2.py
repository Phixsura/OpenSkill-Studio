from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_rel_v2 import fleet_ai_platform_reliability_v2
def test_prv2():
    r = fleet_ai_platform_reliability_v2([{"active": True, "uptime_pct": 99.999, "incidents_30d": 2, "mttr_min": 8, "budget_pct": 75}])
    assert r["uptime"] == 99.999
    assert r["reliable"]
