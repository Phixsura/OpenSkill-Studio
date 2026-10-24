from app.services.app_marketplace_app_app_connection_pool import ConnectionPoolStats

def test_acquire_release():
    pool = ConnectionPoolStats(min_size=2, max_size=5)
    r = pool.acquire()
    assert r["acquired"]
    assert pool.active == 1
    pool.release()
    assert pool.active == 0

def test_pool_exhausted():
    pool = ConnectionPoolStats(min_size=1, max_size=2)
    pool.acquire()
    pool.acquire()
    r = pool.acquire()
    assert not r["acquired"]
    assert pool.waiting == 1

def test_waiting_served():
    pool = ConnectionPoolStats(min_size=1, max_size=1)
    pool.acquire()
    pool.acquire()  # waiting
    assert pool.waiting == 1
    pool.release()  # serves waiter
    assert pool.waiting == 0
    assert pool.active == 1

def test_stats():
    pool = ConnectionPoolStats(min_size=5, max_size=10)
    pool.acquire()
    pool.acquire()
    s = pool.stats()
    assert s["active"] == 2
    assert s["healthy"]
    assert s["utilization_pct"] == 20.0
