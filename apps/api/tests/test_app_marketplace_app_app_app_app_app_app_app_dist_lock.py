from app.services.app_marketplace_app_app_app_app_app_app_app_dist_lock import DistributedLockManager

def test_lock():
    mgr = DistributedLockManager(default_ttl=10)
    r = mgr.acquire("deploy", owner="worker-1", now=0)
    assert r["acquired"]
    token = r["token"]
    r2 = mgr.acquire("deploy", owner="worker-2", now=5)
    assert not r2["acquired"]
    assert r2["reason"] == "locked"
    # Renew by same owner
    r3 = mgr.acquire("deploy", owner="worker-1", now=8)
    assert r3["acquired"]
    assert r3["renewed"]
    mgr.release("deploy", token=token)
    assert mgr.status()["active_locks"] == 0

def test_expired():
    mgr = DistributedLockManager(default_ttl=5)
    mgr.acquire("job", owner="a", now=0)
    r = mgr.acquire("job", owner="b", now=10)
    assert r["acquired"]  # lock expired
