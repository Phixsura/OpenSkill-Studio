from app.services.app_marketplace_app_subscription_manager import create_subscription, cancel_subscription, get_subscription_metrics

def test_create():
    r = create_subscription(user_id="u1", app_id="a1", plan="pro", billing_cycle="yearly")
    assert r["subscription_id"].startswith("sub_")
    assert r["billing_cycle"] == "yearly"
    assert r["status"] == "active"

def test_cancel_end():
    sub = create_subscription(user_id="u1", app_id="a1", plan="pro")
    r = cancel_subscription(subscription=sub, immediate=False)
    assert r["cancel_at_period_end"]
    assert r["status"] == "active"

def test_cancel_immediate():
    sub = create_subscription(user_id="u1", app_id="a1", plan="pro")
    r = cancel_subscription(subscription=sub, immediate=True)
    assert r["status"] == "cancelled"

def test_metrics():
    subs = [{"status": "active", "plan": "pro"}, {"status": "active", "plan": "starter"},
            {"status": "cancelled", "plan": "pro"}]
    r = get_subscription_metrics(subscriptions=subs)
    assert r["active"] == 2
    assert r["churn_rate"] == 33.3
