from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_dora_v3 import fleet_ai_dora_v3
def test_dv3():
    r = fleet_ai_dora_v3([{"freq_day": 100, "lead_min": 5, "fail_pct": 0.5, "mttr_min": 10, "improving": True}])
    assert r["classification"] == "Elite"
    assert r["trend"] == "improving"
