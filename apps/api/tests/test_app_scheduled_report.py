"""Tests for App Scheduled Report — create, generate, enable/disable."""

import pytest

from app.services.app_scheduled_report import AppScheduledReport


class TestCreate:
    def test_create(self):
        s = AppScheduledReport()
        r = s.create_report("inst-1", "r1", "Weekly Summary", "weekly", "pdf", ["admin@x.com"])
        assert r.schedule == "weekly"
        assert r.enabled is True

    def test_invalid_schedule(self):
        s = AppScheduledReport()
        with pytest.raises(ValueError, match="schedule"):
            s.create_report("inst-1", "r1", "X", "hourly", "pdf", ["a@b.com"])

    def test_no_recipients(self):
        s = AppScheduledReport()
        with pytest.raises(ValueError, match="recipient"):
            s.create_report("inst-1", "r1", "X", "daily", "pdf", [])

    def test_duplicate(self):
        s = AppScheduledReport()
        s.create_report("inst-1", "r1", "X", "daily", "csv", ["a@b.com"])
        with pytest.raises(ValueError):
            s.create_report("inst-1", "r1", "Y", "weekly", "pdf", ["c@d.com"])


class TestGeneration:
    def test_record(self):
        s = AppScheduledReport()
        s.create_report("inst-1", "r1", "X", "daily", "csv", ["a@b.com"])
        r = s.record_generation("inst-1", "r1", now=1000.0)
        assert r.generation_count == 1
        assert r.last_generated_at == 1000.0


class TestEnableDisable:
    def test_disable(self):
        s = AppScheduledReport()
        s.create_report("inst-1", "r1", "X", "daily", "csv", ["a@b.com"])
        r = s.disable("inst-1", "r1")
        assert r.enabled is False

    def test_enable(self):
        s = AppScheduledReport()
        s.create_report("inst-1", "r1", "X", "daily", "csv", ["a@b.com"])
        s.disable("inst-1", "r1")
        r = s.enable("inst-1", "r1")
        assert r.enabled is True


class TestList:
    def test_enabled_only(self):
        s = AppScheduledReport()
        s.create_report("inst-1", "r1", "A", "daily", "csv", ["a@b.com"])
        s.create_report("inst-1", "r2", "B", "weekly", "pdf", ["a@b.com"])
        s.disable("inst-1", "r2")
        reports = s.list_reports("inst-1", enabled_only=True)
        assert len(reports) == 1


class TestIsolation:
    def test_cross_installation(self):
        s = AppScheduledReport()
        s.create_report("inst-1", "r1", "X", "daily", "csv", ["a@b.com"])
        assert s.list_reports("inst-2") == []
