from app.services.app_marketplace_extension_lock_manager import LockManager


def test_acquire_and_release():
    lm = LockManager()
    lock, status = lm.acquire("ext-1:config", "deployer-1")
    assert lock is not None
    assert status == "Acquired"
    assert lm.is_locked("ext-1:config") is True
    assert lm.release("ext-1:config", "deployer-1") is True
    assert lm.is_locked("ext-1:config") is False


def test_contention():
    lm = LockManager()
    lm.acquire("ext-2:deploy", "user-a")
    lock, status = lm.acquire("ext-2:deploy", "user-b")
    assert lock is None
    assert "locked by user-a" in status


def test_reentrant():
    lm = LockManager()
    lm.acquire("ext-3:config", "user-a")
    lock, status = lm.acquire("ext-3:config", "user-a")
    assert lock is not None
    assert status == "Extended"


def test_wrong_holder_cannot_release():
    lm = LockManager()
    lm.acquire("ext-4:state", "owner")
    assert lm.release("ext-4:state", "imposter") is False


def test_expired_lock():
    lm = LockManager()
    lm.acquire("ext-5:res", "user", ttl=-1.0)  # immediately expired
    assert lm.is_locked("ext-5:res") is False
    # Can acquire after expiry
    lock, _ = lm.acquire("ext-5:res", "user-2")
    assert lock is not None


def test_force_release():
    lm = LockManager()
    lm.acquire("ext-6:critical", "user")
    assert lm.force_release("ext-6:critical") is True
    assert lm.is_locked("ext-6:critical") is False


def test_list_active():
    lm = LockManager()
    lm.acquire("r1", "a")
    lm.acquire("r2", "b")
    lm.release("r2", "b")
    active = lm.list_active_locks()
    assert len(active) == 1
    assert active[0]["resource"] == "r1"


def test_cleanup():
    lm = LockManager()
    lm.acquire("c1", "x", ttl=-1)
    lm.acquire("c2", "y")
    lm.release("c2", "y")
    cleaned = lm.cleanup_expired()
    assert cleaned == 2
