from app.services.app_marketplace_extension_lease_manager import LeaseManagerService
import time


def test_acquire():
    lm = LeaseManagerService()
    lease = lm.acquire("resource-1", "holder-a", ttl_seconds=30)
    assert lease is not None
    assert lease.holder == "holder-a"
    assert lease.fencing_token > 0


def test_double_acquire_same_holder():
    lm = LeaseManagerService()
    l1 = lm.acquire("r", "a")
    l2 = lm.acquire("r", "a")  # same holder → renew
    assert l2 is not None


def test_acquire_blocked():
    lm = LeaseManagerService()
    lm.acquire("r", "a", ttl_seconds=30)
    result = lm.acquire("r", "b")
    assert result is None  # held by a


def test_release_and_reacquire():
    lm = LeaseManagerService()
    lm.acquire("r", "a")
    lm.release("r", "a")
    lease = lm.acquire("r", "b")
    assert lease is not None
    assert lease.holder == "b"


def test_expire_and_reacquire():
    lm = LeaseManagerService()
    lm.acquire("r", "a", ttl_seconds=0.01)
    time.sleep(0.02)
    lease = lm.acquire("r", "b")
    assert lease is not None
    assert lease.holder == "b"


def test_renew():
    lm = LeaseManagerService()
    lm.acquire("r", "a", ttl_seconds=1)
    renewed = lm.renew("r", "a", ttl_seconds=30)
    assert renewed is not None
    assert renewed.renewed_count == 1


def test_renew_wrong_holder():
    lm = LeaseManagerService()
    lm.acquire("r", "a")
    assert lm.renew("r", "b") is None


def test_transfer():
    lm = LeaseManagerService()
    lm.acquire("r", "a")
    transferred = lm.transfer("r", "a", "b")
    assert transferred is not None
    assert transferred.holder == "b"
    assert lm.is_valid("r", "b") is True


def test_fencing_token():
    lm = LeaseManagerService()
    l1 = lm.acquire("r", "a")
    token1 = l1.fencing_token
    lm.release("r", "a")
    l2 = lm.acquire("r", "b")
    assert l2.fencing_token > token1
    assert lm.is_valid("r", "b", l2.fencing_token) is True
    assert lm.is_valid("r", "b", token1) is False  # old token


def test_contention_tracking():
    lm = LeaseManagerService()
    lm.acquire("hot_resource", "a")
    lm.acquire("hot_resource", "b")  # blocked
    lm.acquire("hot_resource", "c")  # blocked
    contention = lm.get_contention()
    assert contention["hot_resource"] == 2


def test_cleanup():
    lm = LeaseManagerService()
    lm.acquire("a", "h", ttl_seconds=0.01)
    lm.acquire("b", "h", ttl_seconds=0.01)
    lm.acquire("c", "h", ttl_seconds=30)
    time.sleep(0.02)
    cleaned = lm.cleanup_expired()
    assert cleaned == 2
    assert len(lm.get_all_leases()) == 1
