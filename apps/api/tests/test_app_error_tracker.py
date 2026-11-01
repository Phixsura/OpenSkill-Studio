"""Tests for App Error Tracker — record, group, resolve."""

import pytest

from app.services.app_error_tracker import AppErrorTracker


class TestRecord:
    def test_record(self):
        t = AppErrorTracker()
        g = t.record("inst-1", "NullPointerException", "api-server")
        assert g.count == 1

    def test_dedup(self):
        t = AppErrorTracker()
        t.record("inst-1", "NullPointerException", "api-server")
        g = t.record("inst-1", "NullPointerException", "api-server")
        assert g.count == 2

    def test_different_errors(self):
        t = AppErrorTracker()
        t.record("inst-1", "NullPointer", "api")
        t.record("inst-1", "IndexError", "worker")
        assert len(t.top_errors("inst-1")) == 2


class TestResolve:
    def test_resolve(self):
        t = AppErrorTracker()
        g = t.record("inst-1", "Error", "api")
        t.resolve("inst-1", g.fingerprint)
        assert t.unresolved("inst-1") == []

    def test_reopen_on_recurrence(self):
        t = AppErrorTracker()
        g = t.record("inst-1", "Error", "api")
        t.resolve("inst-1", g.fingerprint)
        g2 = t.record("inst-1", "Error", "api")
        assert g2.resolved is False


class TestIsolation:
    def test_cross(self):
        t = AppErrorTracker()
        t.record("inst-1", "Error", "api")
        assert t.unresolved("inst-2") == []
