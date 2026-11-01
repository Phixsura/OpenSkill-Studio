from app.services.app_marketplace_app_app_app_app_app_app_app_rate_limit_policy import define_policy, check_rate, reset_buckets

def test_policy():
    p = define_policy("api", 100, burst=120)
    assert p["requests_per_min"] == 100
    assert p["burst"] == 120

def test_rate_check():
    reset_buckets()
    p = define_policy("test", 3, burst=3)
    assert check_rate(p, "u1")["allowed"]
    assert check_rate(p, "u1")["allowed"]
    assert check_rate(p, "u1")["allowed"]
    r = check_rate(p, "u1")
    assert not r["allowed"]
    assert r["retry_after"] > 0
    # Different client unaffected
    assert check_rate(p, "u2")["allowed"]
    reset_buckets()
