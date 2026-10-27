from app.services.app_marketplace_extension_conn_pool_mgr import ConnPoolManagerService, PoolConfig
import time


def test_create_pool():
    mgr = ConnPoolManagerService()
    created = mgr.create_pool(PoolConfig("db", min_size=3, max_size=10))
    assert created == 3


def test_checkout_and_checkin():
    mgr = ConnPoolManagerService()
    mgr.create_pool(PoolConfig("db", min_size=2, max_size=5))
    conn = mgr.checkout("db")
    assert conn is not None
    assert conn.in_use is True
    mgr.checkin(conn.conn_id)
    stats = mgr.get_pool_stats("db")
    assert stats["active"] == 0
    assert stats["idle"] == 2


def test_pool_grows():
    mgr = ConnPoolManagerService()
    mgr.create_pool(PoolConfig("db", min_size=1, max_size=3))
    c1 = mgr.checkout("db")
    c2 = mgr.checkout("db")  # grows pool
    assert c2 is not None
    assert mgr.get_pool_stats("db")["total"] == 2


def test_pool_exhausted():
    mgr = ConnPoolManagerService()
    mgr.create_pool(PoolConfig("db", min_size=1, max_size=2))
    mgr.checkout("db")
    mgr.checkout("db")
    assert mgr.checkout("db") is None  # exhausted


def test_unhealthy_checkin():
    mgr = ConnPoolManagerService()
    mgr.create_pool(PoolConfig("db", min_size=2, max_size=5))
    conn = mgr.checkout("db")
    mgr.checkin(conn.conn_id, healthy=False)
    # Unhealthy connection won't be checked out
    assert mgr.get_pool_stats("db")["unhealthy"] == 1


def test_stale_connection_skipped():
    mgr = ConnPoolManagerService()
    mgr.create_pool(PoolConfig("db", min_size=1, max_size=5, max_idle_seconds=0.01))
    conn = mgr.checkout("db")
    mgr.checkin(conn.conn_id)
    time.sleep(0.02)
    # Original conn is stale, should create new one
    new_conn = mgr.checkout("db")
    assert new_conn is not None
    assert new_conn.conn_id != conn.conn_id


def test_cleanup():
    mgr = ConnPoolManagerService()
    mgr.create_pool(PoolConfig("db", min_size=2, max_size=5))
    conn = mgr.checkout("db")
    mgr.checkin(conn.conn_id, healthy=False)
    removed = mgr.cleanup("db")
    # Should remove unhealthy but maintain min_size
    stats = mgr.get_pool_stats("db")
    assert stats["total"] >= 2


def test_reuse_connection():
    mgr = ConnPoolManagerService()
    mgr.create_pool(PoolConfig("db", min_size=1, max_size=1))
    c1 = mgr.checkout("db")
    mgr.checkin(c1.conn_id)
    c2 = mgr.checkout("db")
    assert c2.conn_id == c1.conn_id
    assert c2.use_count == 2


def test_dashboard():
    mgr = ConnPoolManagerService()
    mgr.create_pool(PoolConfig("db", min_size=2))
    mgr.create_pool(PoolConfig("cache", min_size=1))
    mgr.checkout("db")
    dash = mgr.get_dashboard()
    assert "db" in dash["pools"]
    assert "cache" in dash["pools"]
    assert dash["total_checkouts"] == 1
