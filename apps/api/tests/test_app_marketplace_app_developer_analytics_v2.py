from app.services.app_marketplace_app_developer_analytics_v2 import compute_engagement_score, predict_ltv, build_cohort_table

def test_engagement_power():
    r = compute_engagement_score(daily_active=800, monthly_active=1000, api_calls=100000,
                                  features_used=9, total_features=10)
    assert r["tier"] == "power"
    assert r["dau_mau_ratio"] == 80.0

def test_engagement_casual():
    r = compute_engagement_score(daily_active=10, monthly_active=1000, api_calls=50,
                                  features_used=1, total_features=10)
    assert r["tier"] == "casual"

def test_ltv():
    r = predict_ltv(avg_monthly_revenue=100, churn_rate=5)
    assert r["ltv"] == 2000
    assert r["months"] == 20

def test_ltv_zero_churn():
    r = predict_ltv(avg_monthly_revenue=100, churn_rate=0)
    assert r["months"] == 999

def test_cohort():
    installs = [{"cohort": "2026-01"}, {"cohort": "2026-01"}, {"cohort": "2026-02"}]
    retention = {"2026-01": [100, 80, 60], "2026-02": [100, 90]}
    r = build_cohort_table(installs=installs, retention_data=retention)
    assert len(r) == 2
    assert r[0]["size"] == 2
