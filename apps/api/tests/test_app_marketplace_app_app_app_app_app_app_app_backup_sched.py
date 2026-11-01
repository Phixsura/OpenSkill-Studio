from app.services.app_marketplace_app_app_app_app_app_app_app_backup_sched import (
    create_schedule, create_backup_record, summarize_backups,
)

def test_schedule():
    r = create_schedule("nightly", "daily", retention_days=7, targets=["database", "files"])
    assert r["created"]
    assert r["frequency"] == "daily"
    assert r["next_run"] > 0

def test_backup_and_summary():
    b1 = create_backup_record("nightly", 150.5, 120)
    b2 = create_backup_record("nightly", 155.0, 130)
    assert b1["status"] == "completed"
    s = summarize_backups([b1, b2])
    assert s["total"] == 2
    assert s["total_size_mb"] == 305.5
    assert s["avg_size_mb"] == 152.8

def test_invalid_freq():
    r = create_schedule("bad", "every5min")
    assert not r["created"]
