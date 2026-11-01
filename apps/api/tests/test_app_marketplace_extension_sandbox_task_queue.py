from app.services.app_marketplace_extension_sandbox_task_queue import (
    SandboxTaskQueueService, TaskState,
)


def test_enqueue_and_dequeue():
    svc = SandboxTaskQueueService()
    svc.enqueue("sb-1", "process_data", {"file": "data.csv"})
    task = svc.dequeue("sb-1")
    assert task is not None
    assert task.state == TaskState.RUNNING
    assert task.name == "process_data"


def test_priority_ordering():
    svc = SandboxTaskQueueService()
    svc.enqueue("sb-1", "low", priority=1)
    svc.enqueue("sb-1", "high", priority=10)
    task = svc.dequeue("sb-1")
    assert task.name == "high"


def test_complete():
    svc = SandboxTaskQueueService()
    svc.enqueue("sb-1", "task")
    task = svc.dequeue("sb-1")
    assert svc.complete(task.task_id, {"output": "done"}) is True
    assert task.state == TaskState.COMPLETED
    assert task.progress == 100


def test_fail_with_retry():
    svc = SandboxTaskQueueService()
    svc.enqueue("sb-1", "flaky", max_retries=3)
    task = svc.dequeue("sb-1")
    svc.fail(task.task_id, "timeout")
    assert task.state == TaskState.PENDING  # retrying
    assert task.retry_count == 1


def test_fail_exhausted():
    svc = SandboxTaskQueueService()
    svc.enqueue("sb-1", "broken", max_retries=1)
    task = svc.dequeue("sb-1")
    svc.fail(task.task_id, "crash")
    assert task.state == TaskState.FAILED


def test_dependency():
    svc = SandboxTaskQueueService()
    t1 = svc.enqueue("sb-1", "build")
    t2 = svc.enqueue("sb-1", "deploy", depends_on=t1.task_id)
    assert t2.state == TaskState.WAITING
    # Complete dependency
    task1 = svc.dequeue("sb-1")
    svc.complete(task1.task_id)
    assert t2.state == TaskState.PENDING  # unblocked


def test_progress():
    svc = SandboxTaskQueueService()
    svc.enqueue("sb-1", "long_task")
    task = svc.dequeue("sb-1")
    svc.update_progress(task.task_id, 50)
    assert task.progress == 50


def test_cancel():
    svc = SandboxTaskQueueService()
    task = svc.enqueue("sb-1", "optional")
    assert svc.cancel(task.task_id) is True
    assert task.state == TaskState.CANCELLED


def test_stats():
    svc = SandboxTaskQueueService()
    svc.enqueue("sb-1", "a")
    svc.enqueue("sb-1", "b")
    t = svc.dequeue("sb-1")
    svc.complete(t.task_id)
    stats = svc.get_stats("sb-1")
    assert stats["by_state"]["completed"] == 1
    assert stats["by_state"]["pending"] == 1
