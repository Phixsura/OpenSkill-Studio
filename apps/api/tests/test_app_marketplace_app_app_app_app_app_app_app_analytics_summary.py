from app.services.app_marketplace_app_app_app_app_app_app_app_analytics_summary import compute_analytics

def test_analytics():
    r = compute_analytics(dau=5000, mau=20000, api_calls_today=2500000,
                           revenue_mtd=125000, new_apps_mtd=45,
                           avg_session_min=12.5, nps_score=65,
                           churn_rate_pct=1.8, support_tickets_open=23)
    assert r["dau_mau_ratio"] == 25.0
    assert r["engagement"] == "high"
    assert r["revenue_display"] == "$125,000"
    assert r["health_indicators"][0]["status"] == "excellent"  # NPS 65
    assert r["health_indicators"][1]["status"] == "excellent"  # Churn 1.8
