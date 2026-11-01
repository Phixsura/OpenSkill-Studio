from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_dora_v8 import fleet_ai_dora_v8
def test_dv8():
    r = fleet_ai_dora_v8([{"freq_day": 500, "lead_min": 2, "fail_pct": 0.05, "mttr_min": 3}])
    assert r["class"] == "Elite"
    assert r["elite"]
