from app.services.app_marketplace_app_app_app_app_app_app_app_opex_score import calculate_opex_score

def test_elite():
    r = calculate_opex_score(
        {"deploy_freq_per_day": 3, "lead_time_hours": 2, "mttr_hours": 0.5, "change_failure_rate": 2},
        {"automation_pct": 95, "test_coverage": 90, "doc_coverage": 85})
    assert r["level"] == "elite"
    assert r["overall"] >= 90

def test_medium():
    r = calculate_opex_score(
        {"deploy_freq_per_day": 0.1, "lead_time_hours": 200, "mttr_hours": 48, "change_failure_rate": 20},
        {"automation_pct": 50, "test_coverage": 60, "doc_coverage": 40})
    assert r["level"] in ("medium", "low")
