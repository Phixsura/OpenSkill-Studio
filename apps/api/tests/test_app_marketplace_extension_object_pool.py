from app.services.app_marketplace_extension_object_pool import ObjectPoolService
import time


def test_borrow_and_return():
    pool = ObjectPoolService(min_size=2, max_size=5)
    obj = pool.borrow()
    assert obj is not None
    assert obj.in_use is True
    pool.return_obj(obj.obj_id)
    assert pool._pool[obj.obj_id].in_use is False


def test_pre_fill_min_size():
    pool = ObjectPoolService(min_size=3, max_size=10)
    assert pool.stats()["total_size"] == 3


def test_pool_grows_on_demand():
    pool = ObjectPoolService(min_size=1, max_size=5)
    borrowed = []
    for _ in range(3):
        obj = pool.borrow()
        borrowed.append(obj)
    assert pool.stats()["total_size"] == 3
    assert pool.stats()["active"] == 3


def test_pool_exhausted():
    pool = ObjectPoolService(min_size=1, max_size=2)
    pool.borrow()
    pool.borrow()
    assert pool.borrow() is None  # exhausted


def test_reuse_returned_object():
    pool = ObjectPoolService(min_size=1, max_size=1)
    obj1 = pool.borrow()
    pool.return_obj(obj1.obj_id)
    obj2 = pool.borrow()
    assert obj2.obj_id == obj1.obj_id  # reused
    assert obj2.borrow_count == 2


def test_unhealthy_returned_replaced():
    pool = ObjectPoolService(min_size=2, max_size=5)
    obj = pool.borrow()
    pool.return_obj(obj.obj_id, healthy=False)
    # Should still have min_size objects
    stats = pool.stats()
    assert stats["total_size"] >= 2


def test_validation_on_borrow():
    call_count = 0
    def validator(po):
        nonlocal call_count
        call_count += 1
        return call_count > 1  # first object fails validation
    pool = ObjectPoolService(min_size=2, max_size=5, validator=validator)
    obj = pool.borrow()
    # Should have validated and possibly skipped unhealthy one
    assert obj is not None


def test_idle_eviction():
    pool = ObjectPoolService(min_size=1, max_size=5, max_idle_seconds=0.01)
    obj = pool.borrow()
    pool.return_obj(obj.obj_id)
    time.sleep(0.02)
    pool._evict_idle()
    # Should evict but maintain minimum
    assert pool.stats()["total_size"] >= 1


def test_stats():
    pool = ObjectPoolService(min_size=2, max_size=5)
    pool.borrow()
    stats = pool.stats()
    assert stats["active"] == 1
    assert stats["idle"] >= 1
    assert stats["total_borrows"] == 1
    assert stats["min_size"] == 2
    assert stats["max_size"] == 5
