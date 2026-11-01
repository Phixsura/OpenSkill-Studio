"""Tests for Consumer API Webhook Testing service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_webhook_tester import (
    WebhookTester, TestPayload,
)


class TestWebhookTester:
    def test_create_payload(self):
        svc = WebhookTester()
        result = svc.create_payload(TestPayload("p1", "order.created", {"id": 1}))
        assert result["event_type"] == "order.created"

    def test_run_test_success(self):
        svc = WebhookTester()
        svc.create_payload(TestPayload("p1", "test", {"data": True}))
        result = svc.run_test("t1", "https://hook.com/cb", "p1")
        assert result["success"] is True
        assert result["status_code"] == 200

    def test_run_test_failure(self):
        svc = WebhookTester()
        svc.create_payload(TestPayload("p1", "test", {"data": True}))
        result = svc.run_test("t1", "https://hook.com/cb", "p1", simulated_status=500)
        assert result["success"] is False

    def test_run_test_error(self):
        svc = WebhookTester()
        svc.create_payload(TestPayload("p1", "test", {"data": True}))
        result = svc.run_test("t1", "https://hook.com/cb", "p1", simulated_error="timeout")
        assert result["success"] is False
        assert result["error"] == "timeout"

    def test_run_suite(self):
        svc = WebhookTester()
        svc.create_payload(TestPayload("p1", "a", {"x": 1}))
        svc.create_payload(TestPayload("p2", "b", {"y": 2}))
        result = svc.run_suite("https://hook.com/cb")
        assert result["total"] == 2
        assert result["all_passed"] is True

    def test_get_results(self):
        svc = WebhookTester()
        svc.create_payload(TestPayload("p1", "test", {"x": 1}))
        svc.run_test("t1", "https://a.com", "p1")
        svc.run_test("t2", "https://b.com", "p1")
        results = svc.get_results(webhook_url="https://a.com")
        assert len(results) == 1

    def test_list_payloads(self):
        svc = WebhookTester()
        svc.create_payload(TestPayload("p1", "a", {"x": 1}, "Test A"))
        svc.create_payload(TestPayload("p2", "b", {"y": 2}, "Test B"))
        assert len(svc.list_payloads()) == 2

    def test_stats(self):
        svc = WebhookTester()
        svc.create_payload(TestPayload("p1", "test", {"x": 1}))
        svc.run_test("t1", "https://hook.com", "p1")
        svc.run_test("t2", "https://hook.com", "p1", simulated_status=500)
        stats = svc.get_stats()
        assert stats["passed"] == 1
        assert stats["failed"] == 1
        assert stats["pass_rate"] == 50.0

    def test_missing_payload(self):
        svc = WebhookTester()
        with pytest.raises(ValueError):
            svc.run_test("t1", "https://hook.com", "missing")

    def test_invalid_url(self):
        svc = WebhookTester()
        svc.create_payload(TestPayload("p1", "test", {"x": 1}))
        with pytest.raises(ValueError):
            svc.run_test("t1", "not-a-url", "p1")

    def test_duplicate_payload(self):
        svc = WebhookTester()
        svc.create_payload(TestPayload("p1", "a", {"x": 1}))
        with pytest.raises(ValueError):
            svc.create_payload(TestPayload("p1", "b", {"y": 2}))

    def test_isolation(self):
        a, b = WebhookTester(), WebhookTester()
        a.create_payload(TestPayload("p1", "a", {"x": 1}))
        assert b.list_payloads() == []
