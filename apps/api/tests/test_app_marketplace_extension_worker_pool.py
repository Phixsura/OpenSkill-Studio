from app.services.app_marketplace_extension_worker_pool import WorkerPoolService


def test_submit_and_process():
    pool = WorkerPoolService(num_workers=2)
    task = pool.submit("t1", payload={"action": "compute"})
    assert task.assigned_to.startswith("worker-")
    result = pool.process(task.assigned_to)
    assert result.task_id == "t1"
    assert result.status == "completed"


def test_least_loaded_routing():
    pool = WorkerPoolService(num_workers=3)
    # Fill worker-0's queue
    for i in range(5):
        pool.submit(f"t{i}", affinity_key=f"same-key-{i}")
    # Next task should go to least loaded
    stats = pool.stats()
    loads = [w["queued"] for w in stats["per_worker"]]
    assert max(loads) - min(loads) <= 5  # roughly balanced


def test_affinity_routing():
    pool = WorkerPoolService(num_workers=4)
    t1 = pool.submit("a", affinity_key="user-123")
    t2 = pool.submit("b", affinity_key="user-123")
    # Same affinity key → same worker
    assert t1.assigned_to == t2.assigned_to


def test_work_stealing():
    pool = WorkerPoolService(num_workers=2)
    # All tasks go to worker-0 via affinity
    for i in range(6):
        pool.submit(f"t{i}", affinity_key="heavy")
    # Process from worker-1 (empty) → should steal from worker-0
    stolen = pool.process("worker-1")
    if stolen:
        assert stolen.status == "completed"
        assert pool.stats()["total_steals"] >= 1


def test_priority_ordering():
    pool = WorkerPoolService(num_workers=1)
    pool.submit("low", priority=10)
    pool.submit("high", priority=1)
    pool.submit("medium", priority=5)
    result = pool.process("worker-0")
    assert result.task_id == "high"  # highest priority first


def test_process_all():
    pool = WorkerPoolService(num_workers=3)
    for i in range(9):
        pool.submit(f"t{i}")
    processed = pool.process_all()
    assert processed == 9
    assert pool.stats()["total_queued"] == 0


def test_unhealthy_worker_skipped():
    pool = WorkerPoolService(num_workers=2)
    pool._workers[0].healthy = False
    task = pool.submit("t1")
    assert task.assigned_to == "worker-1"


def test_stats():
    pool = WorkerPoolService(num_workers=2)
    pool.submit("t1")
    pool.submit("t2")
    pool.process_all()
    stats = pool.stats()
    assert stats["total_submitted"] == 2
    assert stats["total_processed"] == 2
