from app.services.app_marketplace_extension_sandbox_conn_pool import SandboxConnPoolService

def test_acquire_and_release():
    svc = SandboxConnPoolService()
    svc.configure("sb-1", "db", 5)
    conn = svc.acquire("sb-1", "db")
    assert conn.state == "active"
    svc.release("sb-1", "db", conn.conn_id)
    assert conn.state == "idle"

def test_reuse_idle():
    svc = SandboxConnPoolService()
    svc.configure("sb-1", "db", 5)
    c1 = svc.acquire("sb-1", "db")
    svc.release("sb-1", "db", c1.conn_id)
    c2 = svc.acquire("sb-1", "db")
    assert c1.conn_id == c2.conn_id

def test_pool_exhaustion():
    svc = SandboxConnPoolService()
    svc.configure("sb-1", "db", 2)
    svc.acquire("sb-1", "db")
    svc.acquire("sb-1", "db")
    result = svc.acquire("sb-1", "db")
    assert isinstance(result, dict) and "exhausted" in result["error"]

def test_stats():
    svc = SandboxConnPoolService()
    svc.configure("sb-1", "db", 10)
    c1 = svc.acquire("sb-1", "db")
    svc.acquire("sb-1", "db")
    svc.release("sb-1", "db", c1.conn_id)
    stats = svc.get_stats("sb-1", "db")
    assert stats["active"] == 1
    assert stats["idle"] == 1
