from app.services.app_marketplace_app_app_cron_history import build_cron_history

def test_history():
    execs = [
        {"job_name": "cleanup", "status": "success", "duration_ms": 500, "started_at": "2026-01-02"},
        {"job_name": "sync", "status": "success", "duration_ms": 1200, "started_at": "2026-01-03"},
        {"job_name": "report", "status": "failed", "duration_ms": 100, "started_at": "2026-01-01"},
    ]
    r = build_cron_history(executions=execs)
    assert r["total"] == 3
    assert r["success"] == 2
    assert r["failed"] == 1
    assert r["success_rate"] == 66.7
    assert r["executions"][0]["job_name"] == "sync"  # newest first
