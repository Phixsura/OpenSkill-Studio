from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_dora_v5 import fleet_ai_dora_v5
def test_dv5():
    r = fleet_ai_dora_v5([{"freq_day": 200, "lead_min": 2, "fail_pct": 0.1, "mttr_min": 5}])
    assert r["class"] == "Elite"
    assert r["elite"]
