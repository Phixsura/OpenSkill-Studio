from app.services.app_marketplace_extension_api_rate_plan import ExtApiRatePlanService

def test_default_free():
    svc = ExtApiRatePlanService()
    plan = svc.get_limits("ext-new")
    assert plan.plan_id == "free"
    assert plan.requests_per_minute == 60

def test_assign():
    svc = ExtApiRatePlanService()
    svc.assign("ext-1", "pro")
    assert svc.get_limits("ext-1").requests_per_minute == 1000

def test_check_limit():
    svc = ExtApiRatePlanService()
    ok, remaining = svc.check_within_limit("ext-1", 50)
    assert ok is True
    assert remaining == 10  # 60 - 50
