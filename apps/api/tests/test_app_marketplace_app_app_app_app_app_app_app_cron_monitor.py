from app.services.app_marketplace_app_app_app_app_app_app_app_cron_monitor import record_execution, analyze_job_health

def test_record():
    r = record_execution("cleanup", True, 5.5, "done")
    assert r["success"]
    assert r["duration_sec"] == 5.5

def test_health():
    execs = [
        record_execution("job", True, 3),
        record_execution("job", True, 4),
        record_execution("job", False, 10),
    ]
    r = analyze_job_health(execs)
    assert r["runs"] == 3
    assert r["success_rate"] == 67
    assert r["consecutive_failures"] == 1
    assert r["healthy"]
