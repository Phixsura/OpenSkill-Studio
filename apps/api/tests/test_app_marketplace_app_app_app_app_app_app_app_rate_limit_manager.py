from app.services.app_marketplace_app_app_app_app_app_app_app_rate_limit_manager import RateLimitManager

def test_rate_limit():
    mgr = RateLimitManager()
    mgr.configure("api_key_1", limit=3, window_sec=60)
    r1 = mgr.check("api_key_1", now=0)
    assert r1["allowed"]
    assert r1["remaining"] == 2
    mgr.check("api_key_1", now=1)
    mgr.check("api_key_1", now=2)
    r4 = mgr.check("api_key_1", now=3)
    assert not r4["allowed"]
    assert r4["reason"] == "rate_limited"
    assert r4["retry_after"] > 0
    s = mgr.stats("api_key_1")
    assert s["blocked"] == 1
    assert s["total_hits"] == 3

def test_unconfigured():
    mgr = RateLimitManager()
    r = mgr.check("unknown_key")
    assert not r["allowed"]
    assert r["reason"] == "unconfigured"
