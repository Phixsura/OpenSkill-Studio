from app.services.app_marketplace_extension_distributed_lock import DistributedLockService
import time


def test_acquire_and_release():
    svc = DistributedLockService()
    lock = svc.acquire("resource-1", "owner-a")
    assert lock is not None
    assert lock.fencing_token > 0
    assert svc.release("resource-1", "owner-a") is True


def test_exclusive_blocks_second_owner():
    svc = DistributedLockService()
    svc.acquire("r1", "owner-a")
    lock2 = svc.acquire("r1", "owner-b")
    assert lock2 is None  # blocked


def test_reentrant_lock():
    svc = DistributedLockService()
    lock1 = svc.acquire("r1", "owner-a")
    lock2 = svc.acquire("r1", "owner-a")  # same owner = renew
    assert lock2 is not None
    assert lock2.renewed_count > 0


def test_lease_expiry():
    svc = DistributedLockService()
    svc.acquire("r1", "owner-a", lease_seconds=0.01)
    time.sleep(0.02)
    # Lock expired — another owner can acquire
    lock = svc.acquire("r1", "owner-b")
    assert lock is not None


def test_fencing_token_increments():
    svc = DistributedLockService()
    l1 = svc.acquire("r1", "a")
    svc.release("r1", "a")
    l2 = svc.acquire("r1", "b")
    assert l2.fencing_token > l1.fencing_token


def test_fencing_token_validation():
    svc = DistributedLockService()
    lock = svc.acquire("r1", "owner-a")
    assert svc.is_valid_fencing_token("r1", lock.fencing_token) is True
    svc.release("r1", "owner-a")
    new_lock = svc.acquire("r1", "owner-b")
    # Old token is no longer valid
    assert svc.is_valid_fencing_token("r1", lock.fencing_token) is False
    assert svc.is_valid_fencing_token("r1", new_lock.fencing_token) is True


def test_shared_locks():
    svc = DistributedLockService()
    s1 = svc.acquire("r1", "reader-a", mode="shared")
    s2 = svc.acquire("r1", "reader-b", mode="shared")
    assert s1 is not None and s2 is not None
    # Exclusive blocked while shared held
    ex = svc.acquire("r1", "writer")
    assert ex is None


def test_shared_blocked_by_exclusive():
    svc = DistributedLockService()
    svc.acquire("r1", "writer", mode="exclusive")
    shared = svc.acquire("r1", "reader", mode="shared")
    assert shared is None


def test_renew():
    svc = DistributedLockService()
    lock = svc.acquire("r1", "owner-a", lease_seconds=1)
    original_expiry = lock.expires_at
    time.sleep(0.01)
    renewed = svc.renew("r1", "owner-a", lease_seconds=30)
    assert renewed is not None
    assert renewed.expires_at > original_expiry


def test_deadlock_detection():
    svc = DistributedLockService()
    # A holds r1, B holds r2
    svc.acquire("r1", "A")
    svc.acquire("r2", "B")
    # A waits for r2 (held by B)
    svc.acquire("r2", "A")
    # B waits for r1 (held by A) — deadlock!
    svc.acquire("r1", "B")
    cycles = svc.detect_deadlock()
    assert cycles is not None


def test_stats():
    svc = DistributedLockService()
    svc.acquire("r1", "a")
    svc.acquire("r2", "b", mode="shared")
    svc.acquire("r2", "c", mode="shared")
    stats = svc.get_stats()
    assert stats["exclusive_locks"] == 1
    assert stats["shared_locks"] == 2
