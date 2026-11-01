"""Tests for App API Webhook Test — record, query."""

from app.services.app_api_webhook_test import AppAPIWebhookTest


class TestRecord:
    def test_success(self):
        t = AppAPIWebhookTest()
        r = t.record_test("inst-1", "t1", "https://a.com", 200, 45.0)
        assert r.success is True

    def test_failure(self):
        t = AppAPIWebhookTest()
        r = t.record_test("inst-1", "t1", "https://a.com", None, 0, "Connection refused")
        assert r.success is False

    def test_last_result(self):
        t = AppAPIWebhookTest()
        t.record_test("inst-1", "t1", "https://a.com", 200, 50)
        t.record_test("inst-1", "t2", "https://a.com", 500, 100)
        last = t.last_result("inst-1", "https://a.com")
        assert last is not None
        assert last.status_code == 500


class TestIsolation:
    def test_cross(self):
        t = AppAPIWebhookTest()
        t.record_test("inst-1", "t1", "https://a.com", 200, 50)
        assert t.last_result("inst-2", "https://a.com") is None
