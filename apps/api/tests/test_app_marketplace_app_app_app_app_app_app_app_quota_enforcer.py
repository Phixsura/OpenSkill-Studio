from app.services.app_marketplace_app_app_app_app_app_app_app_quota_enforcer import QuotaEnforcer

def test_quota():
    e = QuotaEnforcer()
    e.set_quota("api_calls", hard_limit=100, soft_limit=80)
    for _ in range(79):
        r = e.consume("api_calls")
        assert r["allowed"]
    r80 = e.consume("api_calls")
    assert r80["allowed"]
    assert r80["warning"]
    assert r80["reason"] == "soft_limit_warning"
    for _ in range(20):
        e.consume("api_calls")
    r_over = e.consume("api_calls")
    assert not r_over["allowed"]
    assert r_over["reason"] == "hard_limit_exceeded"

def test_reset():
    e = QuotaEnforcer()
    e.set_quota("storage", hard_limit=1000)
    e.consume("storage", 500)
    e.reset("storage")
    s = e.summary()
    assert s["quotas"][0]["usage"] == 0
