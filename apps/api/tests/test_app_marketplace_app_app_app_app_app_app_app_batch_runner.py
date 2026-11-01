from app.services.app_marketplace_app_app_app_app_app_app_app_batch_runner import create_job, process_batch, job_summary

def test_process():
    j = create_job("export", 250, batch_size=100)
    assert j["total_batches"] == 3
    process_batch(j)
    assert j["status"] == "running"
    process_batch(j)
    r = process_batch(j)
    assert r["progress_pct"] == 100
    assert j["status"] == "completed"

def test_summary():
    jobs = [create_job("a", 100), create_job("b", 200)]
    s = job_summary(jobs)
    assert s["total_jobs"] == 2
    assert s["total_items"] == 300
    assert s["pending"] == 2
