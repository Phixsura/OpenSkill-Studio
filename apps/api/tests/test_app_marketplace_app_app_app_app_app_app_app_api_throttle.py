from app.services.app_marketplace_app_app_app_app_app_app_app_api_throttle import ApiThrottleManager

def test_throttle():
    tm = ApiThrottleManager()
    tm.set_quota("t1", requests_per_minute=3)
    for _ in range(3):
        r = tm.check("t1", now=100)
        assert r["allowed"]
    r = tm.check("t1", now=100)
    assert not r["allowed"]

def test_window_reset():
    tm = ApiThrottleManager()
    tm.set_quota("t1", requests_per_minute=1)
    tm.check("t1", now=100)
    assert not tm.check("t1", now=100)["allowed"]
    assert tm.check("t1", now=161)["allowed"]  # new window

def test_report():
    tm = ApiThrottleManager()
    tm.set_quota("t1", requests_per_minute=10)
    for _ in range(5):
        tm.check("t1", now=100)
    r = tm.usage_report()
    assert r["total_tenants"] == 1
    assert r["tenants"][0]["pct_used"] == 50.0
