from app.services.app_marketplace_extension_bulkhead import (
    BulkheadService, BulkheadConfig
)


def test_acquire_and_release():
    bh = BulkheadService()
    bh.create(BulkheadConfig("api", max_concurrent=5))
    token = bh.try_acquire("api")
    assert token is not None
    state = bh.get_state("api")
    assert state["active"] == 1
    bh.release(token)
    assert bh.get_state("api")["active"] == 0


def test_reject_when_full():
    bh = BulkheadService()
    bh.create(BulkheadConfig("api", max_concurrent=2, max_queue=0))
    t1 = bh.try_acquire("api")
    t2 = bh.try_acquire("api")
    t3 = bh.try_acquire("api")  # should be rejected
    assert t1 is not None
    assert t2 is not None
    assert t3 is None
    assert bh.get_state("api")["total_rejected"] == 1


def test_isolation():
    bh = BulkheadService()
    bh.create(BulkheadConfig("critical", max_concurrent=2))
    bh.create(BulkheadConfig("background", max_concurrent=5))
    # Fill critical
    bh.try_acquire("critical")
    bh.try_acquire("critical")
    assert bh.try_acquire("critical") is None  # full
    # Background still available
    assert bh.try_acquire("background") is not None


def test_utilization():
    bh = BulkheadService()
    bh.create(BulkheadConfig("api", max_concurrent=10))
    for _ in range(7):
        bh.try_acquire("api")
    state = bh.get_state("api")
    assert state["utilization"] == 70.0


def test_error_tracking():
    bh = BulkheadService()
    bh.create(BulkheadConfig("api", max_concurrent=10))
    t1 = bh.try_acquire("api")
    t2 = bh.try_acquire("api")
    bh.release(t1, success=True)
    bh.release(t2, success=False)
    state = bh.get_state("api")
    assert state["error_rate"] == 50.0


def test_resize():
    bh = BulkheadService()
    bh.create(BulkheadConfig("api", max_concurrent=5))
    bh.resize("api", 20)
    assert bh.get_state("api")["max_concurrent"] == 20


def test_auto_shrink():
    bh = BulkheadService()
    bh.create(BulkheadConfig("api", max_concurrent=20))
    state = bh._bulkheads["api"]
    state.total_success = 5
    state.total_errors = 15  # 75% error rate
    result = bh.auto_resize("api", target_error_rate=5.0)
    assert result["action"] == "shrink"
    assert result["to"] < 20


def test_auto_grow():
    bh = BulkheadService()
    bh.create(BulkheadConfig("api", max_concurrent=5))
    state = bh._bulkheads["api"]
    state.total_success = 100
    state.total_errors = 1  # 1% error rate
    state.total_rejected = 50  # many rejections
    result = bh.auto_resize("api", target_error_rate=5.0)
    assert result["action"] == "grow"


def test_all_states():
    bh = BulkheadService()
    bh.create(BulkheadConfig("api", max_concurrent=10))
    bh.create(BulkheadConfig("worker", max_concurrent=20))
    states = bh.get_all_states()
    assert "api" in states
    assert "worker" in states
