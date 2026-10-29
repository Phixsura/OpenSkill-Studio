"""Tests for App API Webhook Dead Letter — store, retry, purge."""

from app.services.app_api_webhook_dead_letter import AppAPIWebhookDeadLetter


class TestStore:
    def test_store(self):
        d = AppAPIWebhookDeadLetter()
        dl = d.store("inst-1", "dl1", "https://a.com", "push", "{}", "timeout", 5)
        assert dl.retried is False


class TestRetry:
    def test_mark_retried(self):
        d = AppAPIWebhookDeadLetter()
        d.store("inst-1", "dl1", "https://a.com", "push", "{}", "err", 3)
        d.mark_retried("inst-1", "dl1")
        assert d.pending("inst-1") == []

    def test_pending(self):
        d = AppAPIWebhookDeadLetter()
        d.store("inst-1", "dl1", "https://a.com", "push", "{}", "err", 3)
        d.store("inst-1", "dl2", "https://b.com", "issue", "{}", "err", 5)
        d.mark_retried("inst-1", "dl1")
        assert len(d.pending("inst-1")) == 1


class TestPurge:
    def test_purge(self):
        d = AppAPIWebhookDeadLetter()
        d.store("inst-1", "dl1", "https://a.com", "push", "{}", "err", 3)
        d.mark_retried("inst-1", "dl1")
        removed = d.purge("inst-1")
        assert removed == 1
        assert d.count("inst-1") == 0


class TestIsolation:
    def test_cross(self):
        d = AppAPIWebhookDeadLetter()
        d.store("inst-1", "dl1", "https://a.com", "push", "{}", "err", 3)
        assert d.count("inst-2") == 0
