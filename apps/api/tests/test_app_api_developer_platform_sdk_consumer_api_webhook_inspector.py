"""Tests for Consumer API Webhook Inspector service."""
from app.services.app_api_developer_platform_sdk_consumer_api_webhook_inspector import (
    WebhookInspector, InspectedRequest, InspectedResponse,
)


class TestWebhookInspector:
    def _req(self, rid="r1", wid="wh1"):
        return InspectedRequest(rid, wid, "POST", "https://hook.com/cb", {"Content-Type": "application/json"}, '{"event":"test"}')

    def _resp(self, status=200, latency=50.0):
        return InspectedResponse(status, {}, '{"ok":true}', latency)

    def test_record_and_get(self):
        svc = WebhookInspector()
        svc.record(self._req(), self._resp(), "order.created", "c1")
        record = svc.get_record("r1")
        assert record is not None
        assert record["response_status"] == 200
        assert record["event_type"] == "order.created"

    def test_list_recent(self):
        svc = WebhookInspector()
        svc.record(self._req("r1"), self._resp(), "order.created")
        svc.record(self._req("r2", "wh2"), self._resp(), "user.created")
        recent = svc.list_recent()
        assert len(recent) == 2
        assert recent[0]["request_id"] == "r2"  # most recent first

    def test_filter_by_webhook(self):
        svc = WebhookInspector()
        svc.record(self._req("r1", "wh1"), self._resp())
        svc.record(self._req("r2", "wh2"), self._resp())
        filtered = svc.list_recent(webhook_id="wh1")
        assert len(filtered) == 1

    def test_filter_by_event_type(self):
        svc = WebhookInspector()
        svc.record(self._req("r1"), self._resp(), "order.created")
        svc.record(self._req("r2"), self._resp(), "user.created")
        filtered = svc.list_recent(event_type="order.created")
        assert len(filtered) == 1

    def test_get_failed(self):
        svc = WebhookInspector()
        svc.record(self._req("r1"), self._resp(200))
        svc.record(self._req("r2"), self._resp(500))
        svc.record(self._req("r3"), self._resp(404))
        failed = svc.get_failed()
        assert len(failed) == 2

    def test_no_response(self):
        svc = WebhookInspector()
        svc.record(self._req("r1"))
        record = svc.get_record("r1")
        assert "response_status" not in record

    def test_stats(self):
        svc = WebhookInspector()
        svc.record(self._req("r1"), self._resp(200))
        svc.record(self._req("r2"), self._resp(500))
        svc.record(self._req("r3"))  # no response
        stats = svc.get_stats()
        assert stats["total_inspected"] == 3
        assert stats["with_response"] == 2
        assert stats["failed"] == 1

    def test_eviction(self):
        svc = WebhookInspector()
        svc._max_records = 10
        for i in range(15):
            svc.record(self._req(f"r{i}"), self._resp())
        assert len(svc._records) <= 10

    def test_not_found(self):
        svc = WebhookInspector()
        assert svc.get_record("missing") is None

    def test_isolation(self):
        a, b = WebhookInspector(), WebhookInspector()
        a.record(self._req(), self._resp())
        assert b.get_stats()["total_inspected"] == 0
