from app.services.app_marketplace_app_app_app_app_app_app_app_dist_lock import DistributedLockManager

def test_acquire_release():
    lm = DistributedLockManager(default_ttl=10)
    r = lm.acquire("res-1", "worker-a")
    assert r["acquired"]
    token = r["token"]
    # Same owner can re-acquire
    r2 = lm.acquire("res-1", "worker-a")
    assert r2["acquired"]
    # Different owner blocked
    r3 = lm.acquire("res-1", "worker-b")
    assert not r3["acquired"]
    # Release
    lm.release("res-1", r2["token"])
    r4 = lm.acquire("res-1", "worker-b")
    assert r4["acquired"]

def test_invalid_release():
    lm = DistributedLockManager()
    lm.acquire("res-2", "w1")
    r = lm.release("res-2", "bad-token")
    assert not r["released"]
