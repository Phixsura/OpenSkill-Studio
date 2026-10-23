from app.services.app_marketplace_app_app_app_app_app_app_app_revenue_dashboard import build_revenue_dashboard

def test_revenue():
    r = build_revenue_dashboard(mrr=29000, arr=348000, prev_mrr=25000,
                                 subscribers=1000, churn_rate=2.5,
                                 revenue_by_plan={"pro": 20000, "starter": 6000, "enterprise": 3000})
    assert r["mrr_display"] == "$29,000.00"
    assert r["growth_pct"] == 16.0
    assert r["arpu"] == 29.0
    assert r["by_plan"][0]["plan"] == "pro"
    assert r["growth_trend"] == "up"
