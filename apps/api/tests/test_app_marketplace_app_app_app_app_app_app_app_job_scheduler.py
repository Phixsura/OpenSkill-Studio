from app.services.app_marketplace_app_app_app_app_app_app_app_job_scheduler import JobScheduler

def test_job_lifecycle():
    s = JobScheduler()
    j = s.enqueue(job_type="email", payload={"to": "user@test.com"}, max_retries=2)
    assert j["status"] == "pending"
    r = s.process(j["job_id"], success=False, error="timeout")
    assert r["status"] == "retrying"
    r2 = s.process(j["job_id"], success=False, error="timeout")
    assert r2["status"] == "failed"
    st = s.stats()
    assert st["total"] == 1
    assert st["by_status"]["failed"] == 1

def test_success():
    s = JobScheduler()
    j = s.enqueue(job_type="sync", payload={})
    r = s.process(j["job_id"], success=True)
    assert r["status"] == "completed"
