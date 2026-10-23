from app.services.app_marketplace_usage_quota import get_usage_summary, check_quota

def test_summary():
    usage = {"api_calls": 800, "storage_mb": 50, "webhooks": 3, "team_members": 1}
    r = get_usage_summary(plan="free", usage=usage)
    assert r["plan"] == "free"
    api = next(res for res in r["resources"] if res["resource"] == "api_calls")
    assert api["usage_pct"] == 80.0
    assert api["warning"]

def test_enterprise_unlimited():
    r = get_usage_summary(plan="enterprise", usage={"api_calls": 999999})
    api = next(res for res in r["resources"] if res["resource"] == "api_calls")
    assert api["unlimited"]
    assert not r["any_exceeded"]

def test_check_allowed():
    r = check_quota(plan="starter", resource="api_calls", current=5000)
    assert r["allowed"]
    assert r["remaining"] == 5000

def test_check_exceeded():
    r = check_quota(plan="free", resource="api_calls", current=1000)
    assert not r["allowed"]
    assert r["upgrade_needed"]
