from app.services.app_marketplace_billing_manager import (
    BillingManager, PricingPlan, PricingModel,
)


def test_create_plan_and_subscribe():
    bm = BillingManager()
    plan = bm.create_plan(PricingPlan("plan-1", "ext-1", PricingModel.SUBSCRIPTION, 999))
    assert plan.price_cents == 999
    sub = bm.subscribe("sub-1", "org-1", "plan-1")
    assert sub is not None
    assert sub["status"] == "active"
    assert sub["amount_cents"] == 999


def test_trial_subscription():
    bm = BillingManager()
    bm.create_plan(PricingPlan("plan-2", "ext-2", PricingModel.SUBSCRIPTION, 1999, trial_days=14))
    sub = bm.subscribe("sub-2", "org-2", "plan-2")
    assert sub["status"] == "trial"


def test_cancel():
    bm = BillingManager()
    bm.create_plan(PricingPlan("plan-3", "ext-3", PricingModel.SUBSCRIPTION, 500))
    bm.subscribe("sub-3", "org-3", "plan-3")
    assert bm.cancel_subscription("sub-3") is True
    assert bm.get_subscription("sub-3")["status"] == "canceled"


def test_usage_billing():
    bm = BillingManager()
    bm.create_plan(PricingPlan("plan-4", "ext-4", PricingModel.USAGE_BASED, 0,
                                usage_unit="api_call", usage_price_cents=1))
    bm.subscribe("sub-4", "org-4", "plan-4")
    bm.record_usage("sub-4", 100, "API calls batch 1")
    bm.record_usage("sub-4", 50, "API calls batch 2")
    assert bm.get_usage_total("sub-4") == 150
    invoice = bm.calculate_invoice("sub-4")
    assert invoice["usage_units"] == 150
    assert invoice["usage_amount_cents"] == 150
    assert invoice["total_cents"] == 150


def test_list_org_subscriptions():
    bm = BillingManager()
    bm.create_plan(PricingPlan("plan-5", "ext-5", PricingModel.FREE, 0))
    bm.create_plan(PricingPlan("plan-6", "ext-6", PricingModel.SUBSCRIPTION, 299))
    bm.subscribe("sub-5", "org-5", "plan-5")
    bm.subscribe("sub-6", "org-5", "plan-6")
    subs = bm.list_org_subscriptions("org-5")
    assert len(subs) == 2
