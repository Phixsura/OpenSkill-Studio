from app.services.app_marketplace_app_app_app_app_app_app_app_conn_pool import ConnectionPool

def test_acquire_release():
    pool = ConnectionPool("db", max_size=3, min_size=1)
    r1 = pool.acquire()
    assert r1["acquired"]
    assert not r1["wait"]
    pool.acquire()
    pool.acquire()
    r4 = pool.acquire()  # pool full
    assert not r4["acquired"]
    assert r4["wait"]
    pool.release()
    r5 = pool.acquire()
    assert r5["acquired"]

def test_stats():
    pool = ConnectionPool("cache", max_size=10, min_size=3)
    pool.acquire()
    pool.acquire()
    s = pool.stats()
    assert s["active"] == 2
    assert s["utilization_pct"] == 20.0
