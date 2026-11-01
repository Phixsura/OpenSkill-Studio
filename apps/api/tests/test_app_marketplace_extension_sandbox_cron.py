from app.services.app_marketplace_extension_sandbox_cron import (
    SandboxCronService, CronStatus, parse_expression,
)
import time
import pytest


def test_parse_expression():
    assert parse_expression("every 5m") == 300
    assert parse_expression("every 2h") == 7200
    assert parse_expression("daily 09:00") == 86400


def test_invalid_expression():
    with pytest.raises(ValueError):
        parse_expression("invalid")


def test_register():
    svc = SandboxCronService()
    job = svc.register("sb-1", "cleanup", "every 10m", "rm -rf /tmp/*")
    assert job.interval_seconds == 600
    assert job.status == CronStatus.ACTIVE


def test_min_interval():
    svc = SandboxCronService()
    with pytest.raises(ValueError, match="60 seconds"):
        svc.register("sb-1", "fast", "every 30s", "echo hi")


def test_tick_finds_due():
    svc = SandboxCronService()
    job = svc.register("sb-1", "task", "every 5m", "run")
    # Simulate past due
    job.next_run_at = time.time() - 10
    due = svc.tick()
    assert len(due) == 1


def test_record_run():
    svc = SandboxCronService()
    job = svc.register("sb-1", "sync", "every 1h", "sync")
    svc.record_run(job.job_id)
    assert job.run_count == 1
    assert job.next_run_at > time.time()


def test_auto_disable_on_failures():
    svc = SandboxCronService()
    job = svc.register("sb-1", "flaky", "every 5m", "fail")
    job.max_failures = 3
    for _ in range(3):
        svc.record_run(job.job_id, success=False)
    assert job.status == CronStatus.DISABLED


def test_pause_resume():
    svc = SandboxCronService()
    job = svc.register("sb-1", "task", "every 10m", "run")
    svc.pause(job.job_id)
    assert job.status == CronStatus.PAUSED
    due = svc.tick(now=time.time() + 99999)
    assert len(due) == 0  # paused jobs not returned
    svc.resume(job.job_id)
    assert job.status == CronStatus.ACTIVE


def test_stats():
    svc = SandboxCronService()
    svc.register("sb-1", "a", "every 5m", "a")
    j2 = svc.register("sb-1", "b", "every 1h", "b")
    svc.pause(j2.job_id)
    stats = svc.get_stats("sb-1")
    assert stats["active"] == 1
    assert stats["paused"] == 1
