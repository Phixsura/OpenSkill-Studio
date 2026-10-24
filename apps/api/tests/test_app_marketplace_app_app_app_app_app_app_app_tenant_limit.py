from app.services.app_marketplace_app_app_app_app_app_app_app_tenant_limit import check_limit, tenant_limits_overview

def test_within():
    r = check_limit("t1", "api_calls", 500, 1000)
    assert not r["exceeded"]
    assert not r["warning"]
    assert r["remaining"] == 500

def test_warning():
    r = check_limit("t1", "storage", 85, 100)
    assert r["warning"]

def test_exceeded():
    r = check_limit("t1", "bandwidth", 110, 100)
    assert r["exceeded"]

def test_overview():
    checks = [
        check_limit("t1", "a", 50, 100),
        check_limit("t1", "b", 90, 100),
        check_limit("t1", "c", 110, 100),
    ]
    r = tenant_limits_overview(checks)
    assert r["exceeded"] == 1
    assert r["warnings"] == 1
    assert r["action_needed"]
