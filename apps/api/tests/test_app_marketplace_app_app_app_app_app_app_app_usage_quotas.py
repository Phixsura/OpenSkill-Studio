from app.services.app_marketplace_app_app_app_app_app_app_app_usage_quotas import get_quotas, check_usage

def test_quotas():
    q = get_quotas("pro")
    assert q["limits"]["api_calls"] == 500000
    q2 = get_quotas("enterprise")
    assert q2["limits"]["api_calls"] == "unlimited"

def test_check_exceeded():
    r = check_usage("free", {"api_calls": 1200, "storage_mb": 50, "apps": 2, "webhooks": 3})
    assert r["any_exceeded"]
    assert r["upgrade_suggested"]
    api_check = next(c for c in r["checks"] if c["resource"] == "api_calls")
    assert api_check["exceeded"]

def test_check_ok():
    r = check_usage("pro", {"api_calls": 100, "storage_mb": 10, "apps": 1, "webhooks": 1})
    assert not r["any_exceeded"]
