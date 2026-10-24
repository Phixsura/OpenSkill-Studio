from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_metrics import calculate_dora_metrics

def test_elite():
    r = calculate_dora_metrics({"deploy_frequency_per_day": 5, "lead_time_hours": 2,
                                  "mttr_hours": 0.5, "change_failure_rate_pct": 2})
    assert r["overall"] == "elite"
    assert all(m["level"] == "elite" for m in [r["deploy_frequency"], r["lead_time"], r["mttr"], r["change_failure_rate"]])

def test_mixed():
    r = calculate_dora_metrics({"deploy_frequency_per_day": 0.5, "lead_time_hours": 200,
                                  "mttr_hours": 48, "change_failure_rate_pct": 3})
    assert r["overall"] in ("medium", "high")
