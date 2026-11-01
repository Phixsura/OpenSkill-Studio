from app.services.app_marketplace_revenue_analytics import compute_mrr_trend, compute_revenue_by_plan, forecast_revenue

def test_growing():
    data = [{"mrr_cents": 10000}, {"mrr_cents": 12000}]
    r = compute_mrr_trend(monthly_mrr=data)
    assert r["trend"] == "growing"
    assert r["change_pct"] == 20.0

def test_declining():
    data = [{"mrr_cents": 10000}, {"mrr_cents": 8000}]
    r = compute_mrr_trend(monthly_mrr=data)
    assert r["trend"] == "declining"

def test_by_plan():
    subs = [{"plan": "pro", "monthly_cents": 9900}, {"plan": "starter", "monthly_cents": 2900},
            {"plan": "pro", "monthly_cents": 9900}]
    r = compute_revenue_by_plan(subscriptions=subs)
    assert r[0]["plan"] == "pro"
    assert r[0]["revenue_cents"] == 19800

def test_forecast():
    f = forecast_revenue(current_mrr=10000, growth_rate_pct=10, months=3)
    assert len(f) == 3
    assert f[0]["projected_mrr_cents"] == 11000
    assert f[2]["projected_mrr_cents"] > f[0]["projected_mrr_cents"]
