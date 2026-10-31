"""Tests for Consumer API Webhook Dedup service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_webhook_dedup import WebhookDedup


class TestWebhookDedup:
    def test_first_event_not_duplicate(self):
        svc = WebhookDedup()
        result = svc.check("wh1", "order.created", {"id": 1}, current_time=100)
        assert result["duplicate"] is False

    def test_same_event_is_duplicate(self):
        svc = WebhookDedup()
        svc.check("wh1", "order.created", {"id": 1}, current_time=100)
        result = svc.check("wh1", "order.created", {"id": 1}, current_time=110)
        assert result["duplicate"] is True
        assert result["count"] == 2

    def test_different_payload_not_duplicate(self):
        svc = WebhookDedup()
        svc.check("wh1", "order.created", {"id": 1}, current_time=100)
        result = svc.check("wh1", "order.created", {"id": 2}, current_time=110)
        assert result["duplicate"] is False

    def test_different_event_type_not_duplicate(self):
        svc = WebhookDedup()
        svc.check("wh1", "order.created", {"id": 1}, current_time=100)
        result = svc.check("wh1", "order.updated", {"id": 1}, current_time=110)
        assert result["duplicate"] is False

    def test_ttl_expiry(self):
        svc = WebhookDedup()
        svc.configure(ttl_seconds=60)
        svc.check("wh1", "test", {"id": 1}, current_time=100)
        result = svc.check("wh1", "test", {"id": 1}, current_time=200)
        assert result["duplicate"] is False  # TTL expired

    def test_cleanup(self):
        svc = WebhookDedup()
        svc.configure(ttl_seconds=60)
        svc.check("wh1", "a", {"x": 1}, current_time=100)
        svc.check("wh1", "b", {"y": 2}, current_time=100)
        result = svc.cleanup(current_time=200)
        assert result["removed"] == 2

    def test_recent_dupes(self):
        svc = WebhookDedup()
        for _ in range(5):
            svc.check("wh1", "order.created", {"id": 1}, current_time=100)
        dupes = svc.get_recent_dupes()
        assert len(dupes) == 1
        assert dupes[0]["count"] == 5

    def test_stats(self):
        svc = WebhookDedup()
        svc.check("wh1", "a", {"x": 1}, current_time=100)
        svc.check("wh1", "a", {"x": 1}, current_time=110)
        stats = svc.get_stats()
        assert stats["total_checked"] == 2
        assert stats["total_deduped"] == 1
        assert stats["dedup_rate"] == 50.0

    def test_invalid_ttl(self):
        svc = WebhookDedup()
        with pytest.raises(ValueError):
            svc.configure(ttl_seconds=0)

    def test_isolation(self):
        a, b = WebhookDedup(), WebhookDedup()
        a.check("wh1", "test", {"id": 1})
        assert b.get_stats()["total_checked"] == 0
