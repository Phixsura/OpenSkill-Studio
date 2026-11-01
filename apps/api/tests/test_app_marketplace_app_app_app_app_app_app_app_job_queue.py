from app.services.app_marketplace_app_app_app_app_app_app_app_job_queue import JobQueue

def test_enqueue_dequeue():
    q = JobQueue()
    q.enqueue("j1", {"task": "send_email"}, priority=1)
    q.enqueue("j2", {"task": "resize_image"}, priority=5)
    job = q.dequeue()
    assert job["id"] == "j2"  # higher priority first
    q.complete(job)
    assert q.stats()["completed"] == 1

def test_retry():
    q = JobQueue(max_retries=2)
    q.enqueue("j1", {"task": "test"})
    job = q.dequeue()
    r = q.fail(job, "timeout")
    assert r["status"] == "retrying"
    job2 = q.dequeue()
    r2 = q.fail(job2, "timeout again")
    assert r2["status"] == "failed"
    assert q.stats()["failed"] == 1
