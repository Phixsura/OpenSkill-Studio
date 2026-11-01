from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_supp_v2 import fleet_ai_platform_support_v2
def test_psv2():
    r = fleet_ai_platform_support_v2([{"active": True, "tickets_24h": 500, "resolution_min": 10, "csat": 4.8, "sla_pct": 99}])
    assert r["csat"] == 4.8
    assert r["excellent"]
