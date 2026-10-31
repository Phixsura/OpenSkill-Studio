from app.services.app_marketplace_app_retention_analytics import compute_retention_cohorts, predict_churn_risk, compute_net_retention

def test_cohorts():
    installs = [
        {"installed_at": "2026-01-15T00:00:00Z", "status": "active"},
        {"installed_at": "2026-01-20T00:00:00Z", "status": "uninstalled"},
        {"installed_at": "2026-02-10T00:00:00Z", "status": "active"},
    ]
    r = compute_retention_cohorts(installs=installs)
    assert r["total_months"] == 2
    assert r["cohorts"][0]["retention_rate"] == 50.0

def test_churn_high():
    r = predict_churn_risk(install={"days_since_last_active": 45, "error_count": 15})
    assert r["level"] == "high"

def test_churn_low():
    r = predict_churn_risk(install={"days_since_last_active": 1, "error_count": 0, "webhooks_configured": True})
    assert r["level"] == "low"

def test_net_retention():
    r = compute_net_retention(start_count=100, end_count=110, new_installs=20)
    assert r["net_retention"] == 110.0
    assert r["churned"] == 10
