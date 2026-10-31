"""Tests for Consumer Data Retention service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_data_retention import DataRetentionManager


class TestDataRetentionManager:
    def test_set_and_get_policy(self):
        svc = DataRetentionManager()
        svc.set_policy("c1", "logs", 30)
        policies = svc.get_policies("c1")
        log_policy = next(p for p in policies if p["category"] == "logs")
        assert log_policy["retention_days"] == 30

    def test_auto_purge_due(self):
        svc = DataRetentionManager()
        svc.set_policy("c1", "logs", 30, auto_purge=True)
        svc.set_policy("c1", "audit", 365, auto_purge=False)
        due = svc.get_due_purges("c1")
        assert len(due) == 1
        assert due[0]["category"] == "logs"

    def test_execute_purge(self):
        svc = DataRetentionManager()
        svc.set_policy("c1", "requests", 7)
        result = svc.execute_purge("c1", "requests", "2024-01-15", 500)
        assert result["purged"] is True
        assert result["records_purged"] == 500

    def test_purge_with_archive(self):
        svc = DataRetentionManager()
        svc.set_policy("c1", "analytics", 90, archive_before_purge=True)
        result = svc.execute_purge("c1", "analytics", "2024-01-15", 1000)
        assert result["archived"] is True

    def test_no_policy_purge(self):
        svc = DataRetentionManager()
        result = svc.execute_purge("c1", "logs", "2024-01-15", 100)
        assert result["purged"] is False

    def test_purge_history(self):
        svc = DataRetentionManager()
        svc.set_policy("c1", "logs", 30)
        svc.execute_purge("c1", "logs", "2024-01-01", 100)
        svc.execute_purge("c1", "logs", "2024-02-01", 200)
        history = svc.get_purge_history()
        assert len(history) == 2
        assert history[0]["records_purged"] == 100

    def test_remove_policy(self):
        svc = DataRetentionManager()
        svc.set_policy("c1", "logs", 30)
        result = svc.remove_policy("c1", "logs")
        assert result["removed"] is True
        policies = svc.get_policies("c1")
        log_policy = next(p for p in policies if p["category"] == "logs")
        assert log_policy.get("status") == "no_policy"

    def test_invalid_category(self):
        svc = DataRetentionManager()
        with pytest.raises(ValueError):
            svc.set_policy("c1", "invalid_cat", 30)

    def test_invalid_days(self):
        svc = DataRetentionManager()
        with pytest.raises(ValueError):
            svc.set_policy("c1", "logs", 0)

    def test_stats(self):
        svc = DataRetentionManager()
        svc.set_policy("c1", "logs", 30)
        svc.set_policy("c1", "audit", 365)
        svc.execute_purge("c1", "logs", "2024-01-01", 500)
        stats = svc.get_stats()
        assert stats["total_policies"] == 2
        assert stats["total_records_purged"] == 500

    def test_isolation(self):
        a, b = DataRetentionManager(), DataRetentionManager()
        a.set_policy("c1", "logs", 30)
        assert b.get_due_purges("c1") == []
