"""Tests for App Webhook Delivery Log — attempts, success rate, response time."""

import pytest

from app.services.app_webhook_delivery_log import AppWebhookDeliveryLog


class TestRecordAttempt:
    def test_record(self):
        l = AppWebhookDeliveryLog()
        a = l.record_attempt("inst-1", "a1", "wh-1", "https://x.com/hook", "user.created",
                              status_code=200, success=True, response_time_ms=45)
        assert a.success is True
        assert a.status_code == 200

    def test_failed_attempt(self):
        l = AppWebhookDeliveryLog()
        a = l.record_attempt("inst-1", "a1", "wh-1", "https://x.com/hook", "user.created",
                              success=False, error="connection refused")
        assert a.success is False
        assert a.error == "connection refused"

    def test_missing_url(self):
        l = AppWebhookDeliveryLog()
        with pytest.raises(ValueError, match="url"):
            l.record_attempt("inst-1", "a1", "wh-1", "", "event")


class TestGetAttempts:
    def test_newest_first(self):
        l = AppWebhookDeliveryLog()
        l.record_attempt("inst-1", "a1", "wh-1", "https://x.com", "e", now=1000.0)
        l.record_attempt("inst-1", "a2", "wh-1", "https://x.com", "e", now=1001.0)
        results = l.get_attempts("inst-1")
        assert results[0].attempt_id == "a2"

    def test_filter_by_webhook(self):
        l = AppWebhookDeliveryLog()
        l.record_attempt("inst-1", "a1", "wh-1", "https://x.com", "e")
        l.record_attempt("inst-1", "a2", "wh-2", "https://y.com", "e")
        results = l.get_attempts("inst-1", webhook_id="wh-1")
        assert len(results) == 1

    def test_filter_success_only(self):
        l = AppWebhookDeliveryLog()
        l.record_attempt("inst-1", "a1", "wh-1", "https://x.com", "e", success=True)
        l.record_attempt("inst-1", "a2", "wh-1", "https://x.com", "e", success=False)
        results = l.get_attempts("inst-1", success_only=True)
        assert len(results) == 1

    def test_limit(self):
        l = AppWebhookDeliveryLog()
        for i in range(10):
            l.record_attempt("inst-1", f"a{i}", "wh-1", "https://x.com", "e")
        assert len(l.get_attempts("inst-1", limit=3)) == 3


class TestSuccessRate:
    def test_rate(self):
        l = AppWebhookDeliveryLog()
        l.record_attempt("inst-1", "a1", "wh-1", "https://x.com", "e", success=True)
        l.record_attempt("inst-1", "a2", "wh-1", "https://x.com", "e", success=True)
        l.record_attempt("inst-1", "a3", "wh-1", "https://x.com", "e", success=False)
        assert l.get_success_rate("inst-1") == pytest.approx(66.67, abs=0.01)

    def test_no_attempts(self):
        l = AppWebhookDeliveryLog()
        assert l.get_success_rate("inst-1") == 100.0


class TestAvgResponseTime:
    def test_avg(self):
        l = AppWebhookDeliveryLog()
        l.record_attempt("inst-1", "a1", "wh-1", "https://x.com", "e",
                          success=True, response_time_ms=100)
        l.record_attempt("inst-1", "a2", "wh-1", "https://x.com", "e",
                          success=True, response_time_ms=200)
        assert l.get_avg_response_time("inst-1") == 150.0

    def test_excludes_failed(self):
        l = AppWebhookDeliveryLog()
        l.record_attempt("inst-1", "a1", "wh-1", "https://x.com", "e",
                          success=True, response_time_ms=100)
        l.record_attempt("inst-1", "a2", "wh-1", "https://x.com", "e",
                          success=False, response_time_ms=5000)
        assert l.get_avg_response_time("inst-1") == 100.0


class TestIsolation:
    def test_cross_installation(self):
        l = AppWebhookDeliveryLog()
        l.record_attempt("inst-1", "a1", "wh-1", "https://x.com", "e")
        assert l.count("inst-2") == 0
        assert l.get_attempts("inst-2") == []
