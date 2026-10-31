from app.services.app_marketplace_app_app_app_app_app_app_app_db_backup import DbBackupManager

def test_backup():
    mgr = DbBackupManager()
    b1 = mgr.create_backup(database="primary", size_mb=1500, now=100)
    b2 = mgr.create_backup(database="primary", backup_type="incremental", size_mb=200, now=200)
    mgr.create_backup(database="analytics", size_mb=3000, now=150)
    mgr.verify(b1["id"])
    latest = mgr.latest("primary")
    assert latest["type"] == "incremental"
    s = mgr.retention_summary()
    assert s["total_backups"] == 3
    assert s["by_database"]["primary"] == 2
    assert s["verified_count"] == 1
    assert s["total_size_mb"] == 4700.0
