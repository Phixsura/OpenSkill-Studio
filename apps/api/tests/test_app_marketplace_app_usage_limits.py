from app.services.app_marketplace_app_usage_limits import check_usage_limit, get_plan_limits, check_all_limits

def test_under_limit():
    r = check_usage_limit(current=500, limit=1000, resource="api_calls")
    assert not r["exceeded"]
    assert r["remaining"] == 500

def test_exceeded():
    r = check_usage_limit(current=1000, limit=1000, resource="api_calls")
    assert r["exceeded"]

def test_warning():
    r = check_usage_limit(current=850, limit=1000, resource="api_calls")
    assert r["warning"]

def test_plan_limits():
    free = get_plan_limits(plan="free")
    pro = get_plan_limits(plan="pro")
    assert pro["api_calls"] > free["api_calls"]

def test_check_all():
    r = check_all_limits(usage={"api_calls": 500, "webhooks": 2}, plan="free")
    assert not r["any_exceeded"]

def test_check_all_exceeded():
    r = check_all_limits(usage={"api_calls": 2000}, plan="free")
    assert r["any_exceeded"]
