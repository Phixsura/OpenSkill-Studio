"""Tests for App Data Export Schedule — create, run, due, enable/disable."""

import pytest

from app.services.app_data_export_schedule import AppDataExportSchedule


class TestCreate:
    def test_create(self):
        s = AppDataExportSchedule()
        sched = s.create_schedule("inst-1", "s1", "users", "csv", "s3://bucket/exports", 24, now=1000.0)
        assert sched.interval_hours == 24
        assert sched.next_run_at == 1000.0 + 86400

    def test_invalid_interval(self):
        s = AppDataExportSchedule()
        with pytest.raises(ValueError):
            s.create_schedule("inst-1", "s1", "users", "csv", "s3://x", 0)

    def test_duplicate(self):
        s = AppDataExportSchedule()
        s.create_schedule("inst-1", "s1", "users", "csv", "s3://x", 24)
        with pytest.raises(ValueError):
            s.create_schedule("inst-1", "s1", "orders", "json", "s3://y", 12)


class TestRun:
    def test_record_run(self):
        s = AppDataExportSchedule()
        s.create_schedule("inst-1", "s1", "users", "csv", "s3://x", 24, now=1000.0)
        sched = s.record_run("inst-1", "s1", now=87400.0)
        assert sched.run_count == 1
        assert sched.next_run_at == 87400.0 + 86400

    def test_error_tracking(self):
        s = AppDataExportSchedule()
        s.create_schedule("inst-1", "s1", "users", "csv", "s3://x", 24)
        sched = s.record_run("inst-1", "s1", success=False, error="timeout")
        assert sched.last_error == "timeout"


class TestDue:
    def test_due(self):
        s = AppDataExportSchedule()
        s.create_schedule("inst-1", "s1", "users", "csv", "s3://x", 1, now=1000.0)
        due = s.get_due("inst-1", now=4601.0)
        assert len(due) == 1

    def test_not_due(self):
        s = AppDataExportSchedule()
        s.create_schedule("inst-1", "s1", "users", "csv", "s3://x", 24, now=1000.0)
        assert s.get_due("inst-1", now=2000.0) == []

    def test_disabled_not_due(self):
        s = AppDataExportSchedule()
        s.create_schedule("inst-1", "s1", "users", "csv", "s3://x", 1, now=1000.0)
        s.disable("inst-1", "s1")
        assert s.get_due("inst-1", now=99999.0) == []


class TestIsolation:
    def test_cross_installation(self):
        s = AppDataExportSchedule()
        s.create_schedule("inst-1", "s1", "users", "csv", "s3://x", 24)
        assert s.list_schedules("inst-2") == []
