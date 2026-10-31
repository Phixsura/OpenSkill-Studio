from app.services.app_marketplace_app_app_feature_gate import check_feature, get_plan_limits

def test_allowed():
    r = check_feature(plan="pro", feature="analytics")
    assert r["allowed"]

def test_denied():
    r = check_feature(plan="free", feature="analytics")
    assert not r["allowed"]
    assert r["upgrade_needed"]

def test_limit():
    r = check_feature(plan="free", feature="max_apps")
    assert r["allowed"]
    assert r["limit"] == 5

def test_unlimited():
    r = check_feature(plan="enterprise", feature="max_webhooks")
    assert r["unlimited"]

def test_plan_limits():
    r = get_plan_limits(plan="pro")
    assert r["total"] == 7
