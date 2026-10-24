from app.services.app_marketplace_app_app_app_app_app_app_app_quota_enforce import enforce_quota, quota_overview

def test_enforce():
    r = enforce_quota("t1", "api_calls", 8000, 10000)
    assert r["pct_used"] == 80.0
    assert r["warning"]
    assert not r["exceeded"]
    assert r["remaining"] == 2000

def test_exceeded():
    r = enforce_quota("t2", "storage_gb", 110, 100)
    assert r["exceeded"]

def test_overview():
    quotas = [
        enforce_quota("t1", "a", 50, 100),
        enforce_quota("t1", "b", 90, 100),
        enforce_quota("t1", "c", 110, 100),
    ]
    r = quota_overview(quotas)
    assert r["exceeded"] == 1
    assert r["warnings"] == 1
    assert r["action_needed"]
