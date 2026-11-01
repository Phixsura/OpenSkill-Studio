from app.services.app_marketplace_app_app_backup_scheduler import create_backup_schedule, build_backup_status

def test_create():
    r = create_backup_schedule(name="DB Backup", frequency="daily", retention_days=7)
    assert r["id"].startswith("bak_")
    assert r["cron"] == "0 2 * * *"
    assert r["retention_days"] == 7

def test_status():
    backups = [
        {"id": "1", "status": "completed", "size_mb": 150, "created_at": "2026-01-02"},
        {"id": "2", "status": "completed", "size_mb": 155, "created_at": "2026-01-03"},
        {"id": "3", "status": "failed", "size_mb": 0, "created_at": "2026-01-01"},
    ]
    r = build_backup_status(backups=backups)
    assert r["total"] == 3
    assert r["success_count"] == 2
    assert r["total_size_mb"] == 305
    assert r["latest"]["id"] == "2"  # newest first
