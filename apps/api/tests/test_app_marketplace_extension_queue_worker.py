from app.services.app_marketplace_extension_queue_worker import ExtQueueWorkerService

def test_enqueue_and_dequeue():
    svc = ExtQueueWorkerService()
    svc.enqueue("ext-1", "emails", {"to": "user@example.com"})
    job = svc.dequeue("emails")
    assert job is not None
    assert job.status == "processing"

def test_complete():
    svc = ExtQueueWorkerService()
    svc.enqueue("ext-1", "tasks", {"action": "sync"})
    job = svc.dequeue("tasks")
    svc.complete(job.job_id)
    assert job.status == "completed"

def test_retry():
    svc = ExtQueueWorkerService()
    svc.enqueue("ext-1", "work", {}, max_attempts=2)
    job = svc.dequeue("work")
    svc.fail(job.job_id, "Timeout")
    assert job.status == "pending"  # retried
    job2 = svc.dequeue("work")
    svc.fail(job2.job_id, "Timeout again")
    assert job.status == "dead"  # max attempts reached

def test_stats():
    svc = ExtQueueWorkerService()
    svc.enqueue("ext-1", "q", {})
    svc.enqueue("ext-1", "q", {})
    job = svc.dequeue("q")
    svc.complete(job.job_id)
    stats = svc.get_stats("q")
    assert stats["completed"] == 1
    assert stats["pending"] == 1
