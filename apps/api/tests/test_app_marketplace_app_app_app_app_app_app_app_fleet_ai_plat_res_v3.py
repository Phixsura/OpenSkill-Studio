from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_res_v3 import fleet_ai_platform_resilience_v3
def test_prv3():
    r = fleet_ai_platform_resilience_v3([{"active": True, "blast_radius_pct": 5, "recovery_s": 30, "chaos_score": 95}])
    assert r["chaos_score"] == 95.0
    assert r["resilient"]
