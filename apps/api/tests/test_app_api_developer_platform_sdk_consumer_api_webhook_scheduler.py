"""Tests for Consumer API Webhook Scheduler service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_webhook_scheduler import (
    WebhookScheduler, ScheduledWebhook,
)


class TestWebhookScheduler:
    def test_create_and_execute(self):
        svc = WebhookScheduler()
        svc.create_schedule(ScheduledWebhook("s1", "https://hook.com", "report", "daily"))
        result = svc.execute("s1", "2024-01-01T00:00:00Z")
        assert result["executed"] is True
        assert result["execution_count"] == 1

    def test_once_auto_disables(self):
        svc = WebhookScheduler()
        svc.create_schedule(ScheduledWebhook("s1", "https://hook.com", "alert", "once"))
        svc.execute("s1")
        result = svc.execute("s1")
        assert result["executed"] is False
        assert result["reason"] == "disabled"

    def test_toggle(self):
        svc = WebhookScheduler()
        svc.create_schedule(ScheduledWebhook("s1", "https://hook.com", "test", "hourly"))
        svc.toggle("s1", False)
        assert svc.execute("s1")["executed"] is False
        svc.toggle("s1", True)
        assert svc.execute("s1")["executed"] is True

    def test_cron_requires_expression(self):
        svc = WebhookScheduler()
        with pytest.raises(ValueError):
            svc.create_schedule(ScheduledWebhook("s1", "https://hook.com", "test", "cron"))

    def test_cron_with_expression(self):
        svc = WebhookScheduler()
        svc.create_schedule(ScheduledWebhook("s1", "https://hook.com", "test", "cron",
                                              cron_expression="0 */6 * * *"))
        assert svc.list_schedules()[0]["frequency"] == "cron"

    def test_delete(self):
        svc = WebhookScheduler()
        svc.create_schedule(ScheduledWebhook("s1", "https://hook.com", "test", "daily"))
        assert svc.delete("s1")["deleted"] is True
        assert svc.list_schedules() == []

    def test_get_due(self):
        svc = WebhookScheduler()
        svc.create_schedule(ScheduledWebhook("s1", "https://a.com", "test", "daily"))
        svc.create_schedule(ScheduledWebhook("s2", "https://b.com", "test", "weekly", enabled=False))
        due = svc.get_due()
        assert len(due) == 1

    def test_execution_log(self):
        svc = WebhookScheduler()
        svc.create_schedule(ScheduledWebhook("s1", "https://hook.com", "test", "hourly"))
        svc.execute("s1", "t1")
        svc.execute("s1", "t2")
        log = svc.get_execution_log("s1")
        assert len(log) == 2

    def test_stats(self):
        svc = WebhookScheduler()
        svc.create_schedule(ScheduledWebhook("s1", "https://a.com", "test", "daily"))
        svc.create_schedule(ScheduledWebhook("s2", "https://b.com", "test", "weekly", enabled=False))
        svc.execute("s1")
        stats = svc.get_stats()
        assert stats["enabled"] == 1
        assert stats["total_executions"] == 1

    def test_invalid_frequency(self):
        svc = WebhookScheduler()
        with pytest.raises(ValueError):
            svc.create_schedule(ScheduledWebhook("s1", "https://a.com", "test", "biweekly"))

    def test_invalid_url(self):
        svc = WebhookScheduler()
        with pytest.raises(ValueError):
            svc.create_schedule(ScheduledWebhook("s1", "ftp://a.com", "test", "daily"))

    def test_isolation(self):
        a, b = WebhookScheduler(), WebhookScheduler()
        a.create_schedule(ScheduledWebhook("s1", "https://a.com", "test", "daily"))
        assert b.list_schedules() == []
