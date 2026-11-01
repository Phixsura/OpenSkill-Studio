from app.services.app_marketplace_app_app_app_app_app_app_app_concurrency_lim import ConcurrencyLimiter

def test_acquire_release():
    cl = ConcurrencyLimiter()
    cl.set_limit("api", 2)
    assert cl.acquire("api")["acquired"]
    assert cl.acquire("api")["acquired"]
    r = cl.acquire("api")
    assert not r["acquired"]
    cl.release("api")
    assert cl.acquire("api")["acquired"]

def test_stats():
    cl = ConcurrencyLimiter()
    cl.set_limit("api", 1)
    cl.acquire("api")
    cl.acquire("api")  # rejected
    s = cl.stats()
    assert s["rejected"] == 1
