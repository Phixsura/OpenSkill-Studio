from app.services.app_marketplace_quota_manager import get_quotas, check_quota, compare_plan_quotas

def test_quotas():
    q = get_quotas(plan="pro")
    assert q["apps"] == 25
    assert q["api_calls_per_day"] == 500000

def test_allowed():
    r = check_quota(plan="free", resource="apps", current=0)
    assert r["allowed"]

def test_exceeded():
    r = check_quota(plan="free", resource="apps", current=1)
    assert not r["allowed"]

def test_unlimited():
    r = check_quota(plan="enterprise", resource="apps", current=999)
    assert r["allowed"]
    assert r["unlimited"]

def test_compare():
    c = compare_plan_quotas(current_plan="free", target_plan="pro")
    assert c["comparison"]["apps"]["current"] == 1
    assert c["comparison"]["apps"]["target"] == 25
