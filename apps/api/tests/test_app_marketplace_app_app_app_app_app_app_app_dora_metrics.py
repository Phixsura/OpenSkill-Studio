from app.services.app_marketplace_app_app_app_app_app_app_app_dora_metrics import calculate_dora

def test_elite():
    r = calculate_dora(
        deployments=[{"id": f"d{i}"} for i in range(60)],
        incidents=[{"recovery_hours": 0.5}],
        commits=[{"lead_time_hours": 0.5} for _ in range(60)],
        period_days=30)
    assert r["deployment_frequency"]["label"] == "elite"
    assert r["lead_time"]["label"] == "elite"
    assert r["overall"] in ("elite", "high")

def test_low():
    r = calculate_dora(
        deployments=[{"id": "d1", "caused_incident": True}],
        incidents=[{"recovery_hours": 200}],
        commits=[{"lead_time_hours": 200}],
        period_days=30)
    assert r["change_failure_rate"]["pct"] == 100.0
    assert r["mttr"]["label"] == "low"
