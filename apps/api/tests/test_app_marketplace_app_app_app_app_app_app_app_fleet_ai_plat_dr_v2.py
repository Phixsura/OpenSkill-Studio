from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_dr_v2 import fleet_ai_platform_dr_v2
def test_pdv2():
    r = fleet_ai_platform_dr_v2([{"active": True, "rto_min": 5, "rpo_min": 1, "drills": 4, "regions": 6}])
    assert r["rto_min"] == 5
    assert r["prepared"]
