from app.services.app_marketplace_extension_semaphore import SemaphoreService


def test_create():
    ss = SemaphoreService()
    sem = ss.create("pool", 5)
    assert sem.available == 5
    assert sem.max_permits == 5


def test_acquire_and_release():
    ss = SemaphoreService()
    ss.create("pool", 3)
    assert ss.acquire("pool", "worker-1") is True
    state = ss.get_state("pool")
    assert state["available"] == 2
    assert state["in_use"] == 1
    ss.release("pool", "worker-1")
    assert ss.get_state("pool")["available"] == 3


def test_exhaust():
    ss = SemaphoreService()
    ss.create("pool", 2)
    assert ss.acquire("pool", "a") is True
    assert ss.acquire("pool", "b") is True
    assert ss.acquire("pool", "c") is False  # no permits
    assert ss.get_state("pool")["total_rejected"] == 1


def test_try_acquire():
    ss = SemaphoreService()
    ss.create("pool", 1)
    r1 = ss.try_acquire("pool", "a")
    assert r1["acquired"] is True
    r2 = ss.try_acquire("pool", "b")
    assert r2["acquired"] is False
    assert r2["remaining"] == 0


def test_multi_permit():
    ss = SemaphoreService()
    ss.create("pool", 10)
    assert ss.acquire("pool", "batch", count=5) is True
    assert ss.get_state("pool")["available"] == 5
    assert ss.acquire("pool", "batch2", count=6) is False  # not enough


def test_drain():
    ss = SemaphoreService()
    ss.create("pool", 10)
    ss.acquire("pool", "a", 3)
    drained = ss.drain("pool")
    assert drained == 7
    assert ss.get_state("pool")["available"] == 0


def test_utilization():
    ss = SemaphoreService()
    ss.create("pool", 10)
    ss.acquire("pool", "a", 7)
    state = ss.get_state("pool")
    assert state["utilization"] == 70.0


def test_resize_grow():
    ss = SemaphoreService()
    ss.create("pool", 5)
    ss.acquire("pool", "a", 3)
    ss.resize("pool", 10)
    state = ss.get_state("pool")
    assert state["max_permits"] == 10
    assert state["available"] == 7  # 2 + 5 added


def test_resize_shrink():
    ss = SemaphoreService()
    ss.create("pool", 10)
    ss.acquire("pool", "a", 3)
    ss.resize("pool", 5)
    state = ss.get_state("pool")
    assert state["max_permits"] == 5
    assert state["available"] == 2  # 7 - 5 = 2


def test_invalid_permits():
    ss = SemaphoreService()
    try:
        ss.create("bad", 0)
        assert False
    except ValueError:
        pass
