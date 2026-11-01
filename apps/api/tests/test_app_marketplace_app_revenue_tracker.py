from app.services.app_marketplace_app_revenue_tracker import compute_mrr, compute_revenue_growth, build_revenue_summary

def test_mrr():
    subs = [{"status": "active", "plan": "pro", "monthly_amount_cents": 2999},
            {"status": "active", "plan": "starter", "monthly_amount_cents": 999},
            {"status": "cancelled", "plan": "pro", "monthly_amount_cents": 2999}]
    r = compute_mrr(subscriptions=subs)
    assert r["mrr_cents"] == 3998
    assert r["arr_cents"] == 3998 * 12

def test_growth_up():
    r = compute_revenue_growth(current_mrr=5000, previous_mrr=4000)
    assert r["direction"] == "up"
    assert r["growth_pct"] == 25.0

def test_growth_zero():
    r = compute_revenue_growth(current_mrr=100, previous_mrr=0)
    assert r["growth_pct"] == 100

def test_summary():
    s = build_revenue_summary(mrr_cents=100000, total_customers=50, churn_rate=5)
    assert "$1,000" in s["mrr"]
    assert s["customers"] == 50
