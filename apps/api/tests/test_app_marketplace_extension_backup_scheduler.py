from app.services.app_marketplace_extension_backup_scheduler import BackupScheduler


def test_create_schedule():
    bs = BackupScheduler()
    sched = bs.create_schedule("ext-1", "org-1", "daily", 7)
    assert sched.frequency == "daily"
    assert sched.retention_count == 7
    assert sched.enabled is True


def test_run_backup():
    bs = BackupScheduler()
    sched = bs.create_schedule("ext-2", "org-1")
    record = bs.run_backup(sched.schedule_id, 1024)
    assert record.status == "success"
    assert record.size_bytes == 1024
    assert bs.get_schedule(sched.schedule_id).total_backups == 1


def test_retention():
    bs = BackupScheduler()
    sched = bs.create_schedule("ext-3", "org-1", retention=3)
    for _ in range(5):
        bs.run_backup(sched.schedule_id)
    backups = bs.get_backups(sched.schedule_id)
    assert len(backups) == 3


def test_disable_enable():
    bs = BackupScheduler()
    sched = bs.create_schedule("ext-4", "org-1")
    bs.disable_schedule(sched.schedule_id)
    assert bs.get_schedule(sched.schedule_id).enabled is False
    bs.enable_schedule(sched.schedule_id)
    assert bs.get_schedule(sched.schedule_id).enabled is True


def test_health():
    bs = BackupScheduler()
    sched = bs.create_schedule("ext-5", "org-1")
    bs.run_backup(sched.schedule_id)
    bs.run_backup(sched.schedule_id)
    bs.record_failure(sched.schedule_id)
    health = bs.get_health(sched.schedule_id)
    assert health["total_backups"] == 2
    assert health["failed_backups"] == 1
    assert health["stored_backups"] == 2


def test_list_schedules():
    bs = BackupScheduler()
    bs.create_schedule("ext-6", "org-1")
    bs.create_schedule("ext-6", "org-2")
    bs.create_schedule("ext-7", "org-1")
    assert len(bs.list_schedules("ext-6")) == 2
    assert len(bs.list_schedules()) == 3
