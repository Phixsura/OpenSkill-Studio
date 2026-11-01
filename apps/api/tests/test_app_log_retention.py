"""Tests for App Log Retention — policies, usage, cleanup."""

import pytest

from app.services.app_log_retention import AppLogRetention


class TestCreatePolicy:
    def test_create(self):
        r = AppLogRetention()
        p = r.create_policy("inst-1", "p1", "access", 30, max_size_mb=500)
        assert p.retention_days == 30
        assert p.max_size_mb == 500

    def test_duplicate(self):
        r = AppLogRetention()
        r.create_policy("inst-1", "p1", "access", 30)
        with pytest.raises(ValueError, match="already exists"):
            r.create_policy("inst-1", "p1", "error", 7)

    def test_invalid_days(self):
        r = AppLogRetention()
        with pytest.raises(ValueError, match="retention_days"):
            r.create_policy("inst-1", "p1", "access", 0)


class TestUsage:
    def test_update(self):
        r = AppLogRetention()
        r.create_policy("inst-1", "p1", "access", 30)
        p = r.update_usage("inst-1", "p1", size_mb=250, entry_count=100000)
        assert p.current_size_mb == 250
        assert p.entry_count == 100000

    def test_total_size(self):
        r = AppLogRetention()
        r.create_policy("inst-1", "p1", "access", 30)
        r.create_policy("inst-1", "p2", "error", 7)
        r.update_usage("inst-1", "p1", 200, 0)
        r.update_usage("inst-1", "p2", 50, 0)
        assert r.total_size_mb("inst-1") == 250


class TestCleanup:
    def test_needs_cleanup(self):
        r = AppLogRetention()
        r.create_policy("inst-1", "p1", "access", 30, max_size_mb=100)
        r.update_usage("inst-1", "p1", 150, 50000)
        assert r.needs_cleanup("inst-1", "p1") is True

    def test_no_cleanup_needed(self):
        r = AppLogRetention()
        r.create_policy("inst-1", "p1", "access", 30, max_size_mb=100)
        r.update_usage("inst-1", "p1", 50, 10000)
        assert r.needs_cleanup("inst-1", "p1") is False

    def test_unlimited_never_needs(self):
        r = AppLogRetention()
        r.create_policy("inst-1", "p1", "access", 30)  # max_size_mb=0
        r.update_usage("inst-1", "p1", 9999, 0)
        assert r.needs_cleanup("inst-1", "p1") is False

    def test_record_cleanup(self):
        r = AppLogRetention()
        r.create_policy("inst-1", "p1", "access", 30)
        r.update_usage("inst-1", "p1", 200, 50000)
        p = r.record_cleanup("inst-1", "p1", removed_entries=20000, freed_mb=80, now=1000.0)
        assert p.entry_count == 30000
        assert p.current_size_mb == 120
        assert p.last_cleanup_at == 1000.0


class TestIsolation:
    def test_cross_installation(self):
        r = AppLogRetention()
        r.create_policy("inst-1", "p1", "access", 30)
        with pytest.raises(KeyError):
            r.get_policy("inst-2", "p1")
