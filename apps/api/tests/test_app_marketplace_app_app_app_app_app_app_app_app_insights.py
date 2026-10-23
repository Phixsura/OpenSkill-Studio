from app.services.app_marketplace_app_app_app_app_app_app_app_app_insights import build_insights

def test_insights():
    r = build_insights(app_id="myapp", installs_7d=150, api_calls_7d=500000,
                         errors_7d=50, avg_rating=4.7, reviews_7d=25,
                         active_users=3200, churn_pct=1.5)
    assert r["health"] == "excellent"
    assert r["error_rate"] == 0.01
    assert len(r["kpis"]) == 6
    assert r["kpis"][0]["display"] == "+150"
