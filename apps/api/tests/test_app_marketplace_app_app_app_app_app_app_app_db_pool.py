from app.services.app_marketplace_app_app_app_app_app_app_app_db_pool import ConnectionPool

def test_pool():
    pool = ConnectionPool(max_size=3, min_size=2)
    r1 = pool.acquire()
    assert r1["acquired"]
    assert r1["active"] == 1
    pool.acquire()
    pool.acquire()
    r4 = pool.acquire()
    assert not r4["acquired"]
    assert r4["reason"] == "pool_exhausted"
    pool.release()
    s = pool.stats()
    assert s["active"] == 2
    assert s["waits"] == 1
    assert s["health"] == "healthy"  # 66.7% < 70 threshold
