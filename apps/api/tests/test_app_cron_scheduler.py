"""Tests for App Cron Scheduler — registration, runs, due tasks."""

import pytest

from app.services.app_cron_scheduler import AppCronScheduler, TaskStatus


class TestRegisterTask:
    def test_register(self):
        s = AppCronScheduler()
        t = s.register_task("inst-1", "t1", "Sync Data", "every 5 min", 300, now=1000.0)
        assert t.task_id == "t1"
        assert t.interval_seconds == 300
        assert t.next_run_at == 1300.0
        assert t.status == TaskStatus.ENABLED

    def test_duplicate(self):
        s = AppCronScheduler()
        s.register_task("inst-1", "t1", "Task", "hourly", 3600)
        with pytest.raises(ValueError, match="already exists"):
            s.register_task("inst-1", "t1", "Task2", "hourly", 3600)

    def test_invalid_interval(self):
        s = AppCronScheduler()
        with pytest.raises(ValueError, match="interval"):
            s.register_task("inst-1", "t1", "Task", "bad", 0)


class TestRecordRun:
    def test_success_run(self):
        s = AppCronScheduler()
        s.register_task("inst-1", "t1", "Task", "5min", 300, now=1000.0)
        r = s.record_run("inst-1", "t1", success=True, duration_ms=150, now=1300.0)
        assert r.success is True
        t = s.get_task("inst-1", "t1")
        assert t.run_count == 1
        assert t.last_run_at == 1300.0
        assert t.next_run_at == 1600.0

    def test_failed_run(self):
        s = AppCronScheduler()
        s.register_task("inst-1", "t1", "Task", "5min", 300, now=1000.0)
        r = s.record_run("inst-1", "t1", success=False, error="timeout", now=1300.0)
        assert r.success is False
        t = s.get_task("inst-1", "t1")
        assert t.last_error == "timeout"

    def test_success_clears_error(self):
        s = AppCronScheduler()
        s.register_task("inst-1", "t1", "Task", "5min", 300, now=1000.0)
        s.record_run("inst-1", "t1", success=False, error="fail", now=1300.0)
        s.record_run("inst-1", "t1", success=True, now=1600.0)
        t = s.get_task("inst-1", "t1")
        assert t.last_error is None


class TestEnableDisable:
    def test_disable(self):
        s = AppCronScheduler()
        s.register_task("inst-1", "t1", "Task", "5min", 300)
        t = s.disable_task("inst-1", "t1")
        assert t.status == TaskStatus.DISABLED

    def test_enable(self):
        s = AppCronScheduler()
        s.register_task("inst-1", "t1", "Task", "5min", 300)
        s.disable_task("inst-1", "t1")
        t = s.enable_task("inst-1", "t1")
        assert t.status == TaskStatus.ENABLED


class TestDueTasks:
    def test_due(self):
        s = AppCronScheduler()
        s.register_task("inst-1", "t1", "Task", "5min", 300, now=1000.0)
        due = s.get_due_tasks("inst-1", now=1301.0)
        assert len(due) == 1

    def test_not_due(self):
        s = AppCronScheduler()
        s.register_task("inst-1", "t1", "Task", "5min", 300, now=1000.0)
        due = s.get_due_tasks("inst-1", now=1200.0)
        assert len(due) == 0

    def test_disabled_not_due(self):
        s = AppCronScheduler()
        s.register_task("inst-1", "t1", "Task", "5min", 300, now=1000.0)
        s.disable_task("inst-1", "t1")
        due = s.get_due_tasks("inst-1", now=1301.0)
        assert len(due) == 0


class TestRunHistory:
    def test_history(self):
        s = AppCronScheduler()
        s.register_task("inst-1", "t1", "Task", "5min", 300, now=1000.0)
        s.record_run("inst-1", "t1", now=1300.0)
        s.record_run("inst-1", "t1", now=1600.0)
        h = s.get_run_history("inst-1", "t1")
        assert len(h) == 2
        assert h[0].completed_at == 1600.0  # newest first


class TestIsolation:
    def test_cross_installation(self):
        s = AppCronScheduler()
        s.register_task("inst-1", "t1", "Task", "5min", 300)
        with pytest.raises(KeyError):
            s.get_task("inst-2", "t1")
