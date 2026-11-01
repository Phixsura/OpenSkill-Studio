from app.services.app_marketplace_app_app_app_app_app_app_app_cron_manager import CronJobManager

def test_cron():
    mgr = CronJobManager()
    mgr.schedule(job_id="j1", name="Cleanup", schedule="0 * * * *", command="cleanup.sh")
    mgr.schedule(job_id="j2", name="Report", schedule="0 9 * * 1", command="report.py")
    mgr.record_run("j1", success=True, duration_ms=500)
    mgr.record_run("j1", success=True, duration_ms=450)
    mgr.record_run("j1", success=False, duration_ms=100)
    jobs = mgr.list_jobs()
    j1 = next(j for j in jobs if j["id"] == "j1")
    assert j1["run_count"] == 3
    assert j1["fail_count"] == 1
    assert j1["success_rate"] == 67

def test_toggle():
    mgr = CronJobManager()
    mgr.schedule(job_id="j1", name="X", schedule="* * * * *", command="x")
    r = mgr.toggle("j1")
    assert not r["enabled"]
    r2 = mgr.toggle("j1")
    assert r2["enabled"]
