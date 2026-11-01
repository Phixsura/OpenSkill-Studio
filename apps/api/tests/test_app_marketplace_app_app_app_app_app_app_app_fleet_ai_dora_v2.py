from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_dora_v2 import fleet_ai_dora_metrics_v2
def test_dv2():
    r = fleet_ai_dora_metrics_v2([{"deploy_freq_day": 50, "lead_time_min": 10, "fail_pct": 1, "mttr_min": 15}])
    assert r["classification"] == "Elite"
    assert r["elite"]
