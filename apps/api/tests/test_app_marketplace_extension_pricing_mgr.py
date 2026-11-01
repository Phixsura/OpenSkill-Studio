from app.services.app_marketplace_extension_pricing_mgr import ExtPricingMgrService

def test_create_plans():
    svc = ExtPricingMgrService()
    svc.create_plan("ext-1", "free", "Free", 0, features=["Basic"])
    svc.create_plan("ext-1", "pro", "Pro", 999, features=["Basic", "Advanced"], trial_days=14)
    plans = svc.get_plans("ext-1")
    assert len(plans) == 2

def test_cheapest():
    svc = ExtPricingMgrService()
    svc.create_plan("ext-1", "free", "Free", 0)
    svc.create_plan("ext-1", "pro", "Pro", 999)
    svc.create_plan("ext-1", "enterprise", "Enterprise", 4999)
    assert svc.get_cheapest("ext-1").plan_id == "pro"
    assert svc.has_free_tier("ext-1") is True

def test_deactivate():
    svc = ExtPricingMgrService()
    svc.create_plan("ext-1", "pro", "Pro", 999)
    svc.deactivate("ext-1", "pro")
    assert len(svc.get_plans("ext-1")) == 0

def test_format_price():
    svc = ExtPricingMgrService()
    assert svc.format_price(0) == "Free"
    assert svc.format_price(999) == "$9.99"
    assert svc.format_price(4999) == "$49.99"
