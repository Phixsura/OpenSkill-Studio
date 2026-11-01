from app.services.app_marketplace_app_app_app_app_app_app_app_backup_mgr import BackupManager

def test_create_list():
    bm = BackupManager(retention_days=7)
    bm.create_backup("db-2026-10-24", 512.5, "full")
    bm.create_backup("db-2026-10-24-inc", 50.0, "incremental")
    assert len(bm.list_backups()) == 2
    assert len(bm.list_backups("full")) == 1
    s = bm.stats()
    assert s["total_size_mb"] == 562.5

def test_cleanup():
    bm = BackupManager(retention_days=1)
    bm.create_backup("old", 100)
    r = bm.cleanup_expired(now=time.time() + 86400 * 2)
    assert r["removed"] == 1

import time
