from app.services.app_marketplace_app_app_app_app_app_app_app_limit_enforcer import check_limits

def test_within_limits():
    r = check_limits("free", {"apps": 2, "api_calls_daily": 500})
    assert not r["exceeded"]
    assert r["next_plan"] is None

def test_exceeded():
    r = check_limits("free", {"apps": 5, "api_calls_daily": 2000})
    assert r["exceeded"]
    assert r["upgrade_needed"]
    assert r["next_plan"] == "starter"

def test_enterprise():
    r = check_limits("enterprise", {"apps": 999, "api_calls_daily": 99999999})
    assert not r["exceeded"]
