from app.services.app_marketplace_extension_connector_sync import (
    ConnectorSyncService, SyncDirection, SyncStatus, ConflictResolution,
)


def test_create_and_start():
    svc = ConnectorSyncService()
    job = svc.create_job("ext-1", "slack", "jira")
    result = svc.start_sync(job.job_id)
    assert result["ok"] is True
    assert job.status == SyncStatus.SYNCING


def test_progress_and_complete():
    svc = ConnectorSyncService()
    job = svc.create_job("ext-1", "a", "b")
    svc.start_sync(job.job_id)
    svc.record_progress(job.job_id, synced=50, cursor="page2")
    svc.record_progress(job.job_id, synced=30)
    svc.complete_sync(job.job_id)
    assert job.status == SyncStatus.COMPLETED
    assert job.records_synced == 80
    assert job.cursor == "page2"


def test_conflict_detection():
    svc = ConnectorSyncService()
    job = svc.create_job("ext-1", "a", "b")
    svc.start_sync(job.job_id)
    svc.record_progress(job.job_id, synced=10, conflicts=3)
    svc.complete_sync(job.job_id)
    assert job.status == SyncStatus.CONFLICT


def test_resolve_conflicts():
    svc = ConnectorSyncService()
    job = svc.create_job("ext-1", "a", "b")
    svc.start_sync(job.job_id)
    svc.record_progress(job.job_id, conflicts=2)
    svc.complete_sync(job.job_id)
    assert svc.resolve_conflicts(job.job_id) is True
    assert job.status == SyncStatus.COMPLETED


def test_fail_sync():
    svc = ConnectorSyncService()
    job = svc.create_job("ext-1", "a", "b")
    svc.start_sync(job.job_id)
    svc.fail_sync(job.job_id, "Connection timeout")
    assert job.status == SyncStatus.FAILED
    assert job.error == "Connection timeout"


def test_no_double_start():
    svc = ConnectorSyncService()
    job = svc.create_job("ext-1", "a", "b")
    svc.start_sync(job.job_id)
    result = svc.start_sync(job.job_id)
    assert result["ok"] is False


def test_sync_health():
    svc = ConnectorSyncService()
    j1 = svc.create_job("ext-1", "a", "b")
    svc.start_sync(j1.job_id)
    svc.record_progress(j1.job_id, synced=100)
    svc.complete_sync(j1.job_id)
    j2 = svc.create_job("ext-1", "c", "d")
    svc.start_sync(j2.job_id)
    svc.fail_sync(j2.job_id, "err")
    health = svc.get_sync_health("ext-1")
    assert health["completed"] == 1
    assert health["failed"] == 1
    assert health["total_synced"] == 100
