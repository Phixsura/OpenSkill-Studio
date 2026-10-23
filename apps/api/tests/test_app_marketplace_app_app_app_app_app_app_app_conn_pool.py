from app.services.app_marketplace_app_app_app_app_app_app_app_conn_pool import (
    create_pool, pool_status, acquire, release,
)

def test_acquire_release():
    p = create_pool("main", max_size=3, min_size=1)
    r1 = acquire(p)
    assert r1["acquired"] and r1["source"] == "idle"
    r2 = acquire(p)
    assert r2["acquired"] and r2["source"] == "new"
    release(p)
    s = pool_status(p)
    assert s["active"] == 1
    assert s["health"] == "healthy"

def test_exhausted():
    p = create_pool("tiny", max_size=1, min_size=1)
    acquire(p)  # take the idle one
    r = acquire(p)  # pool full
    assert not r["acquired"]
    assert r["waiting"] == 1
