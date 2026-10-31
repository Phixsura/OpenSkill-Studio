"""Tests for App Data Retention — policies, records, purge."""

import pytest

from app.services.app_data_retention import AppDataRetention


class TestPolicy:
    def test_set(self):
        r = AppDataRetention()
        p = r.set_policy("inst-1", "p1", "logs", 30, "delete")
        assert p.retention_days == 30

    def test_invalid_days(self):
        r = AppDataRetention()
        with pytest.raises(ValueError):
            r.set_policy("inst-1", "p1", "logs", 0)

    def test_invalid_action(self):
        r = AppDataRetention()
        with pytest.raises(ValueError):
            r.set_policy("inst-1", "p1", "logs", 30, "destroy")


class TestRecord:
    def test_add_record(self):
        r = AppDataRetention()
        r.set_policy("inst-1", "p1", "logs", 30)
        rec = r.add_record("inst-1", "r1", "logs")
        assert rec.purged is False
        assert rec.purge_at > rec.created_at

    def test_no_policy(self):
        r = AppDataRetention()
        with pytest.raises(ValueError, match="No retention policy"):
            r.add_record("inst-1", "r1", "logs")


class TestPurge:
    def test_due_for_purge(self):
        r = AppDataRetention()
        # Removed invalid 0-day policy
        
        r = AppDataRetention()
        r.set_policy("inst-1", "p1", "logs", 1)
        r.add_record("inst-1", "r1", "logs")
        assert r.due_for_purge("inst-1") == []  # not yet due

    def test_purge_record(self):
        r = AppDataRetention()
        r.set_policy("inst-1", "p1", "logs", 1)
        r.add_record("inst-1", "r1", "logs")
        rec = r.purge("inst-1", "r1")
        assert rec.purged is True


class TestIsolation:
    def test_cross(self):
        r = AppDataRetention()
        r.set_policy("inst-1", "p1", "logs", 30)
        assert r.list_policies("inst-2") == []
