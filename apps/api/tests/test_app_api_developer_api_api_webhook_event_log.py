import pytest
from app.services.app_api_developer_api_api_webhook_event_log import AppAPIDeveloperAPIApiWebhookEventLog

class TestWebhookEventLog:
    def test_append(self):
        l = AppAPIDeveloperAPIApiWebhookEventLog()
        e = l.append("inst-1", "e1", "push", "https://a.com", "delivered", 512)
        assert e.status == "delivered"

    def test_search_by_type(self):
        l = AppAPIDeveloperAPIApiWebhookEventLog()
        l.append("inst-1", "e1", "push", "https://a.com", "delivered", 100)
        l.append("inst-1", "e2", "issue", "https://a.com", "delivered", 200)
        assert len(l.search("inst-1", event_type="push")) == 1

    def test_search_by_status(self):
        l = AppAPIDeveloperAPIApiWebhookEventLog()
        l.append("inst-1", "e1", "push", "https://a.com", "delivered", 100)
        l.append("inst-1", "e2", "push", "https://a.com", "failed", 100)
        assert len(l.search("inst-1", status="failed")) == 1

    def test_summary(self):
        l = AppAPIDeveloperAPIApiWebhookEventLog()
        l.append("inst-1", "e1", "push", "https://a.com", "delivered", 100)
        l.append("inst-1", "e2", "push", "https://a.com", "delivered", 100)
        l.append("inst-1", "e3", "push", "https://a.com", "failed", 100)
        s = l.summary("inst-1")
        assert s["delivered"] == 2
        assert s["failed"] == 1

    def test_isolation(self):
        l = AppAPIDeveloperAPIApiWebhookEventLog()
        l.append("inst-1", "e1", "push", "https://a.com", "delivered", 100)
        assert l.total("inst-2") == 0
