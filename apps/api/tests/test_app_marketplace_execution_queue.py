from app.services.app_marketplace_execution_queue import (
    ExecutionQueue, ExecutionJob, JobStatus,
)


def test_enqueue_dequeue():
    eq = ExecutionQueue()
    eq.enqueue(ExecutionJob("j1", "ext-1", priority=5, payload={"cmd": "run"}))
    job = eq.dequeue()
    assert job is not None
    assert job.job_id == "j1"
    assert job.status == JobStatus.RUNNING


def test_priority_ordering():
    eq = ExecutionQueue()
    eq.enqueue(ExecutionJob("low", "ext-1", priority=10, payload={}))
    eq.enqueue(ExecutionJob("high", "ext-1", priority=1, payload={}))
    eq.enqueue(ExecutionJob("mid", "ext-1", priority=5, payload={}))
    first = eq.dequeue()
    assert first.job_id == "high"


def test_concurrency_limit():
    eq = ExecutionQueue(max_concurrent=2)
    eq.enqueue(ExecutionJob("a", "ext-1", 1, {}))
    eq.enqueue(ExecutionJob("b", "ext-1", 1, {}))
    eq.enqueue(ExecutionJob("c", "ext-1", 1, {}))
    eq.dequeue()
    eq.dequeue()
    third = eq.dequeue()
    assert third is None  # blocked by concurrency


def test_complete():
    eq = ExecutionQueue()
    eq.enqueue(ExecutionJob("j2", "ext-1", 1, {}))
    eq.dequeue()
    assert eq.complete("j2", {"output": "done"}) is True
    assert eq.get_job("j2").status == JobStatus.COMPLETED
    assert eq.get_running_count() == 0


def test_fail():
    eq = ExecutionQueue()
    eq.enqueue(ExecutionJob("j3", "ext-1", 1, {}))
    eq.dequeue()
    assert eq.fail("j3", "OOM killed") is True
    assert eq.get_job("j3").error == "OOM killed"


def test_cancel():
    eq = ExecutionQueue()
    eq.enqueue(ExecutionJob("j4", "ext-1", 1, {}))
    assert eq.cancel("j4") is True
    assert eq.get_job("j4").status == JobStatus.CANCELED


def test_stats():
    eq = ExecutionQueue(max_concurrent=5)
    eq.enqueue(ExecutionJob("s1", "ext-1", 1, {}))
    eq.enqueue(ExecutionJob("s2", "ext-1", 2, {}))
    eq.dequeue()
    stats = eq.get_stats()
    assert stats["running"] == 1
    assert stats["queue_depth"] == 1
    assert stats["max_concurrent"] == 5
