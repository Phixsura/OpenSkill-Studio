from app.services.app_marketplace_app_app_app_app_app_app_app_data_sync import (
    create_sync_job, update_progress, sync_summary,
)

def test_sync():
    j = create_sync_job("postgres", "elasticsearch", 1000)
    r = update_progress(j, 500)
    assert r["progress_pct"] == 50
    update_progress(j, 490, failed=10)
    assert j["status"] == "completed_with_errors"

def test_summary():
    jobs = [create_sync_job("a", "b", 100), create_sync_job("c", "d", 200)]
    jobs[0]["synced"] = 100
    jobs[0]["status"] = "completed"
    r = sync_summary(jobs)
    assert r["total_records"] == 300
    assert r["running"] == 1
